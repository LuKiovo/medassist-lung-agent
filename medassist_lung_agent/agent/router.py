from dataclasses import dataclass

from medassist_lung_agent.safety.medical_safety import assess_urgency, detect_red_flags


@dataclass
class AgentDecision:
    intent: str
    urgency: str
    red_flags: list[str]
    next_actions: list[str]
    follow_up_questions: list[str]


INTENT_KEYWORDS = {
    "xray_consult": ["胸片", "x光", "X光", "肺片", "影像", "肺炎", "报告", "ct", "CT"],
    "medication": ["吃什么药", "用什么药", "退烧药", "退热药", "布洛芬", "对乙酰氨基酚", "抗生素", "止泻药"],
    "gi": ["肠胃炎", "胃肠炎", "腹泻", "拉肚子", "呕吐", "腹痛", "恶心"],
    "food_safety": ["螃蟹", "西瓜", "海鲜", "过敏", "食物中毒", "能不能吃"],
    "respiratory": ["咳嗽", "咳痰", "发烧", "发热", "气短", "呼吸困难", "胸痛"],
}


def classify_intent(question: str) -> str:
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in question for keyword in keywords):
            return intent
    return "general_health"


def _next_actions(intent: str, urgency: str) -> list[str]:
    if urgency == "emergency":
        return ["停止线上自我判断，尽快急诊或呼叫当地急救电话。", "准备好年龄、基础病、用药、过敏史和症状开始时间。"]
    if urgency == "urgent":
        return ["建议尽快线下就医或咨询医生/药师。", "继续观察症状变化，若加重按急症处理。"]
    if intent == "xray_consult":
        return ["如有胸片图片，可使用右侧胸片分析模块辅助筛查。", "AI 结果需结合医生阅片和临床症状。"]
    if intent == "medication":
        return ["先确认年龄、体重、过敏史、基础病和正在服用的药。", "不要重复使用含相同成分的复方药。"]
    if intent == "gi":
        return ["优先关注补液和脱水风险。", "血便、持续高热、剧烈腹痛或无法进水时及时就医。"]
    return ["先按低风险健康科普建议处理。", "若症状持续、加重或属于高风险人群，请线下就医。"]


def _follow_up_questions(intent: str) -> list[str]:
    base = ["你的年龄是多少？", "症状持续多久了？", "有没有基础病、过敏史或正在服用的药？"]
    if intent == "respiratory":
        return base + ["体温多少？有没有胸痛、气短、咳血或血氧下降？"]
    if intent == "gi":
        return base + ["一天腹泻/呕吐几次？有没有血便、黑便、尿少或明显口渴？"]
    if intent == "medication":
        return base + ["准备使用的药名和规格是什么？是否已经吃过其他感冒药或退热药？"]
    if intent == "xray_consult":
        return base + ["有没有发热、咳嗽、胸痛、呼吸困难？胸片是正位片还是报告截图？"]
    return base


def plan_consultation(question: str) -> AgentDecision:
    intent = classify_intent(question)
    red_flags = detect_red_flags(question)
    urgency = assess_urgency(question, red_flags)
    return AgentDecision(
        intent=intent,
        urgency=urgency,
        red_flags=red_flags,
        next_actions=_next_actions(intent, urgency),
        follow_up_questions=_follow_up_questions(intent),
    )

