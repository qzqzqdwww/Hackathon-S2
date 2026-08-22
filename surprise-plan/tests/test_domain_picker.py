"""Tests for surprise_plan.backend.domain_picker."""
import pytest

from surprise_plan.backend.domain_picker import DOMAINS, pick_domain, _distance_score


class TestDomainPool:
    """Verify the domain pool integrity."""

    def test_domain_count(self):
        """Pool should have ~160 domains."""
        assert len(DOMAINS) >= 150
        assert len(DOMAINS) == 159

    def test_no_duplicates(self):
        """Every domain entry should be unique."""
        assert len(DOMAINS) == len(set(DOMAINS))

    def test_all_have_chinese_and_english(self):
        """Each domain should follow '中文 (English)' format."""
        for d in DOMAINS:
            assert "(" in d, f"Missing English name: {d}"
            assert d.endswith(")"), f"Missing closing paren: {d}"
            chinese = d.split("(")[0].strip()
            assert chinese, f"Empty Chinese name: {d}"

    def test_no_empty_entries(self):
        """No empty strings in the domain pool."""
        assert all(d.strip() for d in DOMAINS)


class TestPickDomain:
    """Test domain selection and exclusion logic."""

    def test_excludes_matching_keyword_english(self):
        """English keyword 'cryptography' should exclude 密码学."""
        result = pick_domain(["cryptography"])
        assert "密码学" not in result["domain"]

    def test_excludes_matching_keyword_chinese(self):
        """Chinese keyword '陶艺' should exclude 陶艺 (Pottery)."""
        result = pick_domain(["陶艺"])
        assert "陶艺" not in result["domain"]

    def test_excludes_multiple_keywords(self):
        """Multiple interests should all be excluded."""
        result = pick_domain(["AI", "音乐", "摄影"])
        domain = result["domain"]
        # None of the excluded topics should appear
        for kw in ["AI", "人工智能", "音乐", "Music", "摄影", "Photo"]:
            assert kw.lower() not in domain.lower(), (
                f"Domain '{domain}' should not contain excluded keyword '{kw}'"
            )

    def test_excludes_domain_matching_keyword(self):
        """'cryptography' in excluded list should exclude 密码学."""
        result = pick_domain(["cryptography", "密码学"])
        assert "密码学" not in result["domain"]
        assert "密码学历史" not in result["domain"]

    def test_returns_dict_with_keys(self):
        """Result should have 'domain' and 'surprise_score' keys."""
        result = pick_domain(["AI"])
        assert "domain" in result
        assert "surprise_score" in result

    def test_surprise_score_positive(self):
        """Surprise score should be at least 1."""
        result = pick_domain(["AI"])
        assert result["surprise_score"] >= 1

    def test_fallback_when_all_excluded(self):
        """If all domains are excluded, fallback picks from full pool."""
        # Exclude everything by using a very common character that appears in many names
        result = pick_domain(["学"])
        # Should not crash; returns some domain with score 0
        assert "domain" in result

    def test_excludes_art_keywords(self):
        """Art-related keywords should exclude art domains."""
        result = pick_domain(["art", "painting", "sculpture"])
        domain = result["domain"]
        art_domains = ["雕塑", "版画", "纤维艺术", "数字媒体艺术", "服装设计",
                        "陶艺", "玻璃吹制", "漆艺", "织物设计", "概念艺术"]
        for art in art_domains:
            assert art not in domain, f"Art domain '{art}' should be excluded"


class TestDistanceScore:
    """Test the semantic distance scoring."""

    def test_base_score(self):
        """Unrelated domain should get base score of 10."""
        score = _distance_score("bee", set())
        assert score == 10

    def test_same_field_penalty(self):
        """Domain in same field as excluded keyword gets -3 penalty.

        'biology' is in science_kw; 'microbiology' contains 'biology' → penalty applies.
        """
        score = _distance_score("microbiology", {"biology"})
        assert score == 7

    def test_no_penalty_different_field(self):
        """Domain in a different field should keep base score."""
        # "bee" matches nothing in any field, so no penalty even if "physics" is excluded
        score = _distance_score("bee", {"physics"})
        assert score == 10

    def test_min_score_is_one(self):
        """Score should never drop below 1."""
        score = _distance_score("ai", {"ai", "software", "programming", "coding"})
        assert score >= 1
