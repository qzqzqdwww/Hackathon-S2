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
    """Pick a random domain NOT semantically close to excluded interests.

    Excludes domains that match any excluded keyword (Chinese or English),
    then uses weighted random to favor domains that are semantically distant.
    """
    import random

    excluded_lower = {kw.lower().strip() for kw in excluded if kw.strip()}

    candidates = []
    for domain in DOMAINS:
        # Extract English keyword from parentheses, e.g. "陶艺 (Pottery)" -> "pottery"
        en_keyword = domain.split("(")[-1].rstrip(")").lower() if "(" in domain else domain.lower()
        # Also check the Chinese/raw name (before the parenthesis)
        raw_name = domain.split("(")[0].strip().lower()

        # Skip if any excluded keyword matches the domain
        if any(kw in en_keyword or kw in raw_name for kw in excluded_lower):
            continue

        score = _distance_score(en_keyword, excluded_lower)
        candidates.append({"domain": domain, "surprise_score": score})

    if not candidates:
        # Fallback: pick randomly from all domains
        domain = random.choice(DOMAINS)
        return {"domain": domain, "surprise_score": 0}

    weights = [c["surprise_score"] + 1 for c in candidates]
    chosen = random.choices(candidates, weights=weights, k=1)[0]
    return chosen


def _distance_score(keyword: str, excluded: set) -> int:
    """Score how semantically distant a domain keyword is from excluded interests.

    Higher score = more surprising (less related to user's interests).
    Base 10, minus 3 for each overlapping conceptual field.
    """
    tech_kw = {"ai", "programming", "software", "coding", "machine learning",
               "data", "web", "app", "computer", "tech", "crypto", "blockchain",
               "code", "developer", "算法", "编程", "代码", "人工智能"}
    art_kw = {"art", "music", "design", "painting", "drawing", "photo", "film",
              "gallery", "sound", "creative", "美术", "音乐", "设计", "摄影"}
    science_kw = {"physics", "chemistry", "biology", "math", "astronomy", "space",
                  "research", "lab", "科学", "生物", "物理", "化学", "天文"}
    craft_kw = {"craft", "making", "build", "wood", "pottery", "weave",
                "手工", "制作", "编织", "陶艺"}

    fields = [tech_kw, art_kw, science_kw, craft_kw]

    def in_field(kw, field):
        return any(f in kw for f in field)

    score = 10
    for field in fields:
        if in_field(keyword, field):
            if any(in_field(ex, field) for ex in excluded):
                score -= 3

    return max(score, 1)
