""" Diverse domain pool for the "Surprise Claude" experience.
    Each domain is a potential learning path that is intentionally
    different from common tech topics, enabling the "breaking filter bubbles"
    mechanic at the heart of Track 03.
"""

DOMAINS = [
    # Crafts & Making
    "陶艺 (Pottery)",
    "折纸 (Origami)",
    "皮革工艺 (Leathercraft)",
    "面具制作 (Mask Making)",
    "微缩模型 (Miniature Making)",
    "绳结艺术 (Macramé)",
    "琥珀加工 (Amber Crafting)",
    "玻璃吹制 (Glassblowing)",
    "制琴 (Luthiery)",

    # Natural World
    "养蜂 (Beekeeping)",
    "真菌学 (Mycology)",
    "鸟类观察 (Birdwatching)",
    "火山学 (Volcanology)",
    "古生物化石 (Paleontology)",
    "樱花栽培 (Sakura Cultivation)",
    "海洋生物学 (Marine Biology)",
    "树木年轮学 (Dendrochronology)",

    # History & Culture
    "密码学历史 (History of Cryptography)",
    "占星学历史 (History of Astrology)",
    "茶道 (Tea Ceremony)",
    "古琴 (Guqin)",
    "制图学历史 (History of Cartography)",
    "古文字学 (Paleography)",
    "香料调制 (Perfumery)",
    "活字印刷 (Letterpress Printing)",

    # Sciences
    "天文学 (Astronomy)",
    "声学 (Acoustics)",
    "材料科学 (Materials Science)",
    "气象学 (Meteorology)",
    "神经美学 (Neuroaesthetics)",
    "量子计算入门 (Quantum Computing)",
    "合成生物学 (Synthetic Biology)",

    # Movement & Practice
    "潜水 (Diving)",
    "驯鹰 (Falconry)",
    "杂技 (Acrobatics)",
    "太极推手 (Tai Chi Push Hands)",
    "陶轮 (Wheel Throwing)",
    "花式跳绳 (Jump Rope)",

    # Food & Fermentation
    "发酵食品 (Fermentation)",
    "康普茶 (Kombucha Brewing)",
    "奶酪制作 (Cheese Making)",
    "Sourdough 烘焙 (Sourdough Baking)",
    "味噌制作 (Miso Making)",

    # Abstract & Play
    "游戏设计哲学 (Game Design Philosophy)",
    "谜题设计 (Puzzle Design)",
    "城市漫游 (Psychogeography / Urban Drifting)",
    "随机 Poetry (Generative Poetry)",
    "声音景观 (Soundscape Art)",
    "数字 Gardening (Digital Gardening)",
]


def pick_domain(excluded: list) -> dict:
    """Pick a random domain that is NOT in the excluded list.

    Parameters
    ----------
    excluded : list[str]
        Domains (or keywords) the user has already stated interest in.

    Returns
    -------
    dict
        {"domain": str, "surprise_score": int}
    """
    import random

    excluded_lower = {kw.lower() for kw in excluded}

    candidates = []
    for domain in DOMAINS:
        keyword = domain.split("(")[-1].rstrip(")").lower() if "(" in domain else domain.lower()
        if keyword not in excluded_lower:
            score = _distance_score(keyword, excluded_lower)
            candidates.append({"domain": domain, "surprise_score": score})

    if not candidates:
        domain = random.choice(DOMAINS)
        return {"domain": domain, "surprise_score": 0}

    weights = [c["surprise_score"] + 1 for c in candidates]
    chosen = random.choices(candidates, weights=weights, k=1)[0]
    return chosen


def _distance_score(keyword: str, excluded: set) -> int:
    """Heuristic distance from excluded keywords."""
    tech_keywords = {"ai", "programming", "software", "coding", "machine learning",
                     "data", "web", "app", "computer", "tech", "crypto", "blockchain"}
    art_keywords = {"art", "music", "design", "painting", "drawing", "photo", "film"}
    science_keywords = {"physics", "chemistry", "biology", "math", "astronomy", "space"}
    craft_keywords = {"craft", "making", "build", "wood", "pottery", "weave"}

    fields = [tech_keywords, art_keywords, science_keywords, craft_keywords]

    def in_field(kw, field):
        return any(f in kw for f in field)

    score = 10
    for field in fields:
        if in_field(keyword, field):
            if any(in_field(ex, field) for ex in excluded):
                score -= 5

    return max(score, 1)
