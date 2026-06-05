from medassist_lung_agent.config import settings
from medassist_lung_agent.llm.qwen_client import generate_with_qwen
from medassist_lung_agent.rag.indexer import build_index, load_index, retrieve
from medassist_lung_agent.safety.medical_safety import detect_red_flags, disclaimer


def _get_index():
    if not settings.rag_index_path.exists():
        return build_index(settings.rag_doc_dir, settings.rag_index_path)
    return load_index(settings.rag_index_path)


def _fallback_answer(question: str, contexts: list[dict], red_flags: list[str]) -> str:
    evidence = "\n".join(f"- {ctx['text'][:260]}" for ctx in contexts[:3])
    urgent = ""
    if red_flags:
        urgent = f"你提到 {', '.join(red_flags)}，这属于需要谨慎处理的信号；若症状明显、加重或属于高风险人群，建议尽快线下就医。\n\n"
    return (
        f"{disclaimer()}\n\n"
        f"{urgent}"
        "根据当前知识库检索到的资料，可以先这样理解：\n"
        f"{evidence}\n\n"
        "建议：补充年龄、体温/症状持续时间、既往病史、正在用药和是否过敏。涉及用药剂量、儿童、孕妇、慢病或症状持续加重时，请咨询医生或药师。"
    )


def answer_health_question(question: str, top_k: int = 4) -> dict:
    index = _get_index()
    contexts = retrieve(question, index, top_k=top_k)
    red_flags = detect_red_flags(question)
    context_text = "\n\n".join(
        f"[来源: {ctx['source']} 分数: {ctx['score']:.3f}]\n{ctx['text']}" for ctx in contexts
    )
    prompt = f"""
你是一个中文医疗健康科普助手。请严格基于检索资料回答，不要编造药物剂量或诊断结论。
必须说明：不能替代医生诊断；出现红旗症状要就医。

用户问题：
{question}

检索资料：
{context_text}

请用中文给出结构清晰、谨慎、可执行的回答。
"""
    answer = generate_with_qwen(prompt) or _fallback_answer(question, contexts, red_flags)
    return {
        "answer": answer,
        "red_flags": red_flags,
        "citations": contexts,
        "medical_disclaimer": disclaimer(),
    }

