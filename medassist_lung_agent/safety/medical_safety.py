RED_FLAG_TERMS = [
    "胸痛",
    "呼吸困难",
    "喘不上气",
    "意识不清",
    "抽搐",
    "昏迷",
    "咯血",
    "血便",
    "黑便",
    "脱水",
    "尿很少",
    "婴儿",
    "孕妇",
    "老人",
    "免疫缺陷",
    "持续高烧",
    "血氧低",
    "口唇发紫",
    "说话不清",
    "肢体无力",
    "呕血",
    "严重腹痛",
    "无法进水",
]

EMERGENCY_TERMS = [
    "呼吸困难",
    "喘不上气",
    "胸痛",
    "意识不清",
    "抽搐",
    "昏迷",
    "口唇发紫",
    "血氧低",
    "说话不清",
    "肢体无力",
    "大量出血",
    "呕血",
]

URGENT_TERMS = [
    "持续高烧",
    "咯血",
    "血便",
    "黑便",
    "严重腹痛",
    "脱水",
    "尿很少",
    "无法进水",
    "孕妇",
    "婴儿",
    "老人",
    "免疫缺陷",
]


def detect_red_flags(question: str) -> list[str]:
    return [term for term in RED_FLAG_TERMS if term in question]


def assess_urgency(question: str, red_flags: list[str] | None = None) -> str:
    if any(term in question for term in EMERGENCY_TERMS):
        return "emergency"
    if any(term in question for term in URGENT_TERMS) or red_flags:
        return "urgent"
    return "routine"


def disclaimer() -> str:
    return "以下内容仅供健康科普和就医前参考，不能替代医生面诊、检查或处方。"
