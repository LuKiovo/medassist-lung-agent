from medassist_lung_agent.config import settings
from medassist_lung_agent.agent.router import plan_consultation
from medassist_lung_agent.llm.qwen_client import generate_with_qwen
from medassist_lung_agent.rag.indexer import build_index, load_index, retrieve
from medassist_lung_agent.safety.medical_safety import disclaimer


def _source_name(source: str) -> str:
    return source.replace("\\", "/").split("/")[-1]


def _clean_follow_up_answers(follow_up_answers: dict[str, str] | None) -> dict[str, str]:
    if not follow_up_answers:
        return {}
    cleaned: dict[str, str] = {}
    for question, answer in follow_up_answers.items():
        q = str(question).strip()
        a = str(answer).strip()
        if q and a:
            cleaned[q] = a[:500]
    return cleaned


def _format_follow_up_answers(follow_up_answers: dict[str, str]) -> str:
    if not follow_up_answers:
        return ""
    lines = [f"- {question} {answer}" for question, answer in follow_up_answers.items()]
    return "用户补充信息：\n" + "\n".join(lines)


def _get_index():
    if not settings.rag_index_path.exists():
        return build_index(settings.rag_doc_dir, settings.rag_index_path)
    return load_index(settings.rag_index_path)


def _common_answer(question: str, red_flags: list[str]) -> str | None:
    urgent = ""
    if red_flags:
        urgent = f"\n\n你提到 {', '.join(red_flags)}，这些属于需要谨慎处理的信号；如果症状明显、持续或加重，建议及时线下就医。"

    if any(word in question for word in ["高烧", "发烧", "发热", "退烧", "退热"]):
        return (
            f"{disclaimer()}\n\n"
            "退烧药不是只按一个固定温度决定，更要看年龄、精神状态、症状持续时间和基础病。\n\n"
            "一般思路：\n"
            "1. 成人如果发热并且明显不舒服，可以按药品说明书考虑使用对乙酰氨基酚或布洛芬这类退热止痛药。\n"
            "2. 如果只是低热、精神状态还可以，可以先休息、补液、观察体温变化。\n"
            "3. 儿童用药要按年龄、体重和说明书，婴幼儿尤其要谨慎；不要把成人药随意减量给儿童。\n"
            "4. 不要同时重复服用多个含相同退热成分的感冒药，避免超量。\n\n"
            "需要尽快就医的情况包括：持续高热不退、呼吸困难、胸痛、意识异常、抽搐、严重脱水，或婴幼儿、孕妇、老人、免疫低下/慢病患者发热。"
            f"{urgent}"
        )

    if any(word in question for word in ["肠胃炎", "胃肠炎", "腹泻", "拉肚子", "呕吐"]):
        return (
            f"{disclaimer()}\n\n"
            "急性胃肠炎多数先看是否脱水，处理重点通常是补液和清淡饮食，而不是一上来就吃抗生素。\n\n"
            "可以先这样做：\n"
            "1. 少量多次补液，腹泻或呕吐明显时优先考虑口服补液盐。\n"
            "2. 暂时吃清淡、易消化食物，避免酒精、油腻、辛辣和生冷刺激。\n"
            "3. 不建议自行长期使用止泻药或抗生素，尤其是有发热、血便时。\n\n"
            "如果出现血便/黑便、持续高热、剧烈腹痛、频繁呕吐喝不进水、尿量明显减少，或患者是儿童、老人、孕妇、免疫低下人群，应及时就医。"
            f"{urgent}"
        )

    if "螃蟹" in question and "西瓜" in question:
        return (
            f"{disclaimer()}\n\n"
            "一般健康成年人吃完螃蟹后少量吃西瓜，通常没有明确医学禁忌。“食物相克”的说法多数缺乏可靠证据。\n\n"
            "真正需要注意的是：\n"
            "1. 螃蟹是否新鲜、是否充分处理，保存不当更容易引起胃肠不适。\n"
            "2. 对海鲜过敏的人不要吃螃蟹。\n"
            "3. 正在腹泻、胃肠功能弱、痛风或尿酸高的人群应少吃或避免海鲜。\n\n"
            "如果吃后出现皮疹、喘息、喉咙发紧、持续呕吐、剧烈腹痛或血便，应及时就医。"
            f"{urgent}"
        )

    return None


def _fallback_answer(question: str, contexts: list[dict], red_flags: list[str], follow_up_answers: dict[str, str] | None = None) -> str:
    cleaned_answers = _clean_follow_up_answers(follow_up_answers)
    supplement = _format_follow_up_answers(cleaned_answers)
    common = _common_answer(question, red_flags)
    if common:
        if supplement:
            return f"{common}\n\n我已参考你补充的信息：\n" + "\n".join(
                f"- {question} {answer}" for question, answer in cleaned_answers.items()
            )
        return common

    evidence = "\n".join(f"- {_source_name(ctx['source'])}: {ctx['text'][:160]}..." for ctx in contexts[:3])
    urgent = ""
    if red_flags:
        urgent = f"你提到 {', '.join(red_flags)}，这属于需要谨慎处理的信号；若症状明显、加重或属于高风险人群，建议尽快线下就医。\n\n"
    return (
        f"{disclaimer()}\n\n"
        f"{urgent}"
        "我先根据知识库给你一个保守的科普建议：\n"
        f"{evidence}\n\n"
        f"{supplement + chr(10) + chr(10) if supplement else ''}"
        "为了判断得更贴近实际，建议补充年龄、症状持续时间、严重程度、既往病史、正在用药和过敏史。涉及具体药物剂量、儿童、孕妇、慢病或症状持续加重时，请咨询医生或药师。"
    )


def answer_health_question(question: str, top_k: int = 4, follow_up_answers: dict[str, str] | None = None) -> dict:
    cleaned_answers = _clean_follow_up_answers(follow_up_answers)
    supplemental_context = _format_follow_up_answers(cleaned_answers)
    retrieval_query = f"{question}\n{supplemental_context}" if supplemental_context else question
    index = _get_index()
    contexts = retrieve(retrieval_query, index, top_k=top_k)
    decision = plan_consultation(question)
    red_flags = decision.red_flags
    context_text = "\n\n".join(
        f"[来源: {ctx['source']} 分数: {ctx['score']:.3f}]\n{ctx['text']}" for ctx in contexts
    )
    prompt = f"""
你是一个中文医疗健康科普助手。请严格基于检索资料回答，不要编造药物剂量或诊断结论。
必须说明：不能替代医生诊断；出现红旗症状要就医。
当前意图分类：{decision.intent}
当前紧急程度：{decision.urgency}

用户问题：
{question}

{supplemental_context}

检索资料：
{context_text}

请用中文给出结构清晰、谨慎、可执行的回答。
"""
    answer = generate_with_qwen(prompt) or _fallback_answer(question, contexts, red_flags, cleaned_answers)
    return {
        "answer": answer,
        "intent": decision.intent,
        "urgency": decision.urgency,
        "next_actions": decision.next_actions,
        "follow_up_questions": decision.follow_up_questions,
        "follow_up_answers": cleaned_answers,
        "supplemental_context": supplemental_context,
        "red_flags": red_flags,
        "citations": contexts,
        "emergency_resources": {
            "phone": "120",
            "human_doctor_url": settings.human_doctor_url,
        },
        "medical_disclaimer": disclaimer(),
    }
