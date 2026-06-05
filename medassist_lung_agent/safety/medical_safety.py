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
]


def detect_red_flags(question: str) -> list[str]:
    return [term for term in RED_FLAG_TERMS if term in question]


def disclaimer() -> str:
    return "以下内容仅供健康科普和就医前参考，不能替代医生面诊、检查或处方。"

