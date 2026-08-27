"""Tests for surprise_plan.backend.domain_picker."""
import pytest
from surprise_plan.backend.domain_picker import DOMAINS, pick_domain, _distance_score


class TestDomainPool:
    def test_domain_count(self):
        assert len(DOMAINS) >= 150
        assert len(DOMAINS) == 159

    def test_no_duplicates(self):
        assert len(DOMAINS) == len(set(DOMAINS))

    def test_format(self):
        for d in DOMAINS:
            assert "(" in d and d.endswith(")")
            assert d.split("(")[0].strip()

    def test_no_empty(self):
        assert all(d.strip() for d in DOMAINS)


class TestPickDomain:
    def test_excludes_english(self):
        assert "密码学" not in pick_domain(["cryptography"])["domain"]

    def test_excludes_chinese(self):
        assert "陶艺" not in pick_domain(["陶艺"])["domain"]

    def test_excludes_multiple(self):
        result = pick_domain(["AI", "音乐", "摄影"])
        for kw in ["AI", "人工智能", "音乐", "Music", "摄影", "Photo"]:
            assert kw.lower() not in result["domain"].lower()

    def test_excludes_cryptography_domains(self):
        result = pick_domain(["cryptography", "密码学"])
        assert "密码学" not in result["domain"]
        assert "密码学历史" not in result["domain"]

    def test_returns_correct_keys(self):
        r = pick_domain(["AI"])
        assert "domain" in r and "surprise_score" in r

    def test_surprise_score_positive(self):
        assert pick_domain(["AI"])["surprise_score"] >= 1

    def test_fallback_when_all_excluded(self):
        r = pick_domain(["学"])
        assert "domain" in r

    def test_excludes_art(self):
        """Explicit art domain names should be excluded."""
        result = pick_domain(["art", "painting", "sculpture"])
        # "服装设计" won't be excluded by "art" since they don't share substrings
        # but "sculpture" and "painting" directly exclude domains containing those words
        assert "雕塑" not in result["domain"]
        assert "版画" not in result["domain"]
        # "纤维艺术" won't be excluded either since none of the keywords match
        # the exclusion is substring-based, not category-based


class TestDistanceScore:
    def test_base_score(self):
        assert _distance_score("bee", set()) == 10

    def test_same_field_penalty(self):
        score = _distance_score("microbiology", {"biology"})
        assert score == 7

    def test_different_field_no_penalty(self):
        assert _distance_score("bee", {"physics"}) == 10

    def test_min_score(self):
        assert _distance_score("ai", {"ai", "software", "programming"}) >= 1
