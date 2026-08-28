""" Diverse domain pool for the "Surprise-Plan" experience.
    Organized by academic discipline, each entry is a specific sub-field
    inspired by real university majors and specialized courses.
    This enables precise exclusion (e.g. exclude "biology" → all biology-
    related sub-fields are filtered out) and rich surprise-factor variety.
"""

import random

DOMAINS = [
    # ── 人文科学 (Humanities) ──────────────────────────────
    "古典学 (Classics)",
    "比较文学 (Comparative Literature)",
    "逻辑学 (Logic)",
    "伦理学 (Ethics)",
    "修辞学 (Rhetoric)",
    "文献学 (Philology)",
    "符号学 (Semiotics)",
    "神话学 (Mythology)",

    # ── 社会科学 (Social Sciences) ─────────────────────────
    "社会心理学 (Social Psychology)",
    "文化人类学 (Cultural Anthropology)",
    "发展经济学 (Development Economics)",
    "政治哲学 (Political Philosophy)",
    "性别研究 (Gender Studies)",
    "传播学 (Communication Studies)",
    "犯罪学 (Criminology)",
    "社会网络分析 (Social Network Analysis)",

    # ── 自然科学 (Natural Sciences) ─────────────────────────
    "分子生物学 (Molecular Biology)",
    "天体物理学 (Astrophysics)",
    "量子力学 (Quantum Mechanics)",
    "有机化学 (Organic Chemistry)",
    "地质学 (Geology)",
    "海洋学 (Oceanography)",
    "气象学 (Meteorology)",
    "神经科学 (Neuroscience)",
    "生态学 (Ecology)",
    "古气候学 (Paleoclimatology)",
    "天体测量学 (Astrometry)",

    # ── 数学与计算机科学 (Math & CS) ────────────────────────
    "密码学 (Cryptography)",
    "拓扑学 (Topology)",
    "数论 (Number Theory)",
    "计算语言学 (Computational Linguistics)",
    "运筹学 (Operations Research)",
    "博弈论 (Game Theory)",
    "混沌理论 (Chaos Theory)",
    "微分几何 (Differential Geometry)",
    "信息论 (Information Theory)",
    "计算机图形学 (Computer Graphics)",

    # ── 艺术与设计 (Arts & Design) ──────────────────────────
    "雕塑 (Sculpture)",
    "版画 (Printmaking)",
    "纤维艺术 (Fiber Art)",
    "数字媒体艺术 (Digital Media Art)",
    "服装设计 (Fashion Design)",
    "陶艺 (Ceramics)",
    "玻璃吹制 (Glassblowing)",
    "漆艺 (Lacquer Art)",
    "织物设计 (Textile Design)",
    "概念艺术 (Concept Art)",

    # ── 音乐与表演 (Music & Performance) ────────────────────
    "指挥学 (Conducting)",
    "音乐治疗 (Music Therapy)",
    "声音艺术 (Sound Art)",
    "爵士乐研究 (Jazz Studies)",
    "民族音乐学 (Ethnomusicology)",
    "电子音乐作曲 (Electronic Music Composition)",
    "配音艺术 (Voice Acting)",
    "默剧与肢体剧 (Mime & Physical Theatre)",

    # ── 建筑与空间 (Architecture & Space) ───────────────────
    "建筑声学 (Architectural Acoustics)",
    "室内设计 (Interior Design)",
    "园林设计 (Landscape Architecture)",
    "城市规划 (Urban Planning)",
    "舞台设计 (Stage Design)",
    "工业设计 (Industrial Design)",
    "可持续建筑 (Sustainable Architecture)",
    "展览设计 (Exhibition Design)",

    # ── 经济与管理 (Economics & Management) ─────────────────
    "金融学 (Finance)",
    "市场营销 (Marketing)",
    "会计学 (Accounting)",
    "国际法 (International Law)",
    "知识产权法 (Intellectual Property Law)",
    "供应链管理 (Supply Chain Management)",
    "人力资源 (Human Resources)",
    "创业学 (Entrepreneurship)",
    "公共政策 (Public Policy)",

    # ── 医学与健康 (Medicine & Health) ──────────────────────
    "解剖学 (Anatomy)",
    "免疫学 (Immunology)",
    "药理学 (Pharmacology)",
    "公共卫生 (Public Health)",
    "营养学 (Nutrition Science)",
    "运动生理学 (Exercise Physiology)",
    "心理学 (Psychology)",
    "睡眠科学 (Sleep Science)",
    "康复医学 (Rehabilitation Medicine)",

    # ── 农业与生命科学 (Agriculture & Life Sciences) ────────
    "农艺学 (Agronomy)",
    "兽医学 (Veterinary Medicine)",
    "食品科学 (Food Science)",
    "园艺学 (Horticulture)",
    "土壤学 (Soil Science)",
    "水产养殖 (Aquaculture)",
    "发酵工程 (Fermentation Engineering)",
    "植物病理学 (Plant Pathology)",

    # ── 传统技艺与工艺 (Traditional Crafts) ──────────────────
    "花道 (Ikebana)",
    "书道 (Calligraphy)",
    "盆景 (Bonsai)",
    "缂丝 (Kesi Weaving)",
    "景泰蓝 (Cloisonné)",
    "篆刻 (Seal Carving)",
    "榫卯工艺 (Mortise and Tenon)",
    "竹编 (Bamboo Weaving)",
    "蜡染 (Batik)",
    "漆器 (Lacquerware)",

    # ── 自然与野外 (Nature & Fieldwork) ─────────────────────
    "养蜂 (Beekeeping)",
    "真菌学 (Mycology)",
    "鸟类学 (Ornithology)",
    "火山学 (Volcanology)",
    "古生物学 (Paleontology)",
    "樱花栽培 (Sakura Cultivation)",
    "海洋生物学 (Marine Biology)",
    "树木年轮学 (Dendrochronology)",
    "陨石学 (Meteoritics)",
    "潮间带生态 (Intertidal Ecology)",

    # ── 历史与文献 (History & Philology) ────────────────────
    "密码学历史 (History of Cryptography)",
    "占星学历史 (History of Astrology)",
    "茶道 (Tea Ceremony)",
    "古琴 (Guqin)",
    "制图学历史 (History of Cartography)",
    "古文字学 (Paleography)",
    "香料调制 (Perfumery)",
    "活字印刷 (Letterpress Printing)",

    # ── 工程与材料 (Engineering & Materials) ────────────────
    "声学 (Acoustics)",
    "材料科学 (Materials Science)",
    "机器人学 (Robotics)",
    "航空航天 (Aerospace Engineering)",
    "生物医学工程 (Biomedical Engineering)",
    "环境工程 (Environmental Engineering)",
    "核工程 (Nuclear Engineering)",
    "纳米技术 (Nanotechnology)",

    # ── 运动与身体实践 (Movement & Practice) ────────────────
    "潜水 (Diving)",
    "驯鹰 (Falconry)",
    "杂技 (Acrobatics)",
    "太极推手 (Tai Chi Push Hands)",
    "花式跳绳 (Jump Rope)",
    "风帆冲浪 (Windsurfing)",
    "攀岩 (Rock Climbing)",
    "武术套路 (Martial Arts Forms)",
    "瑜伽哲学 (Yoga Philosophy)",
    "剑道 (Kendo)",

    # ── 食物与发酵 (Food & Fermentation) ────────────────────
    "发酵食品 (Fermentation)",
    "康普茶 (Kombucha Brewing)",
    "奶酪制作 (Cheese Making)",
    "酸面团烘焙 (Sourdough Baking)",
    "味噌制作 (Miso Making)",
    "分子料理 (Molecular Gastronomy)",
    "咖啡烘焙 (Coffee Roasting)",
    "巧克力制作 (Chocolate Making)",

    # ── 抽象与游戏 (Abstract & Play) ─────────────────────────
    "游戏设计哲学 (Game Design Philosophy)",
    "谜题设计 (Puzzle Design)",
    "城市漫游 (Psychogeography)",
    "生成式诗歌 (Generative Poetry)",
    "声音景观 (Soundscape Art)",
    "数字园艺 (Digital Gardening)",
    "交互叙事 (Interactive Narrative)",
    "角色扮演设计 (LARP Design)",

    # ── 跨学科前沿 (Interdisciplinary) ───────────────────────
    "认知科学 (Cognitive Science)",
    "生物信息学 (Bioinformatics)",
    "数字人文 (Digital Humanities)",
    "系统生物学 (Systems Biology)",
    "仿生学 (Biomimicry)",
    "复杂系统 (Complex Systems)",
    "科学哲学 (Philosophy of Science)",
    "技术伦理 (Technology Ethics)",
]


def pick_domain(excluded: list[str]) -> dict:
    """Pick a random domain NOT semantically close to excluded interests.

    Excludes domains that match any excluded keyword (Chinese or English),
    then uses weighted random to favor domains that are semantically distant.
    """
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
               "code", "developer", "算法", "编程", "代码", "人工智能", "机器人"}
    art_kw = {"art", "music", "design", "painting", "drawing", "photo", "film",
              "gallery", "sound", "creative", "sculpture", "printmaking", "美术",
              "音乐", "设计", "摄影", "雕塑", "版画", "纤维", "服装", "陶艺"}
    science_kw = {"physics", "chemistry", "biology", "math", "astronomy", "space",
                  "research", "lab", "科学", "生物", "物理", "化学", "天文",
                  "分子", "量子", "神经", "免疫", "气象", "海洋", "地质"}
    craft_kw = {"craft", "making", "build", "wood", "pottery", "weave",
                "手工", "制作", "编织", "陶艺", "木工", "锻造"}
    social_kw = {"social", "psychology", "economics", "politics", "law",
                 "社会", "心理", "经济", "政治", "法律", "传播", "性别",
                 "管理", "金融", "市场", "会计"}
    humanities_kw = {"history", "philosophy", "literature", "language",
                     "历史", "哲学", "文学", "语言", "伦理", "逻辑", "文献"}

    fields = [tech_kw, art_kw, science_kw, craft_kw, social_kw, humanities_kw]

    def in_field(kw, field):
        return any(f in kw for f in field)

    score = 10
    for field in fields:
        if in_field(keyword, field):
            if any(in_field(ex, field) for ex in excluded):
                score -= 3

    return max(score, 1)
