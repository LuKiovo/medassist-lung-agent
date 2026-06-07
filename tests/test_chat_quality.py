from medassist_lung_agent.llm.medical_chat import answer_health_question


def test_fever_question_gets_relevant_conversational_answer():
    result = answer_health_question("高烧多少度能吃退烧药", top_k=3)
    answer = result["answer"]
    sources = " ".join(item["source"] for item in result["citations"])
    assert "退烧药" in answer or "退热" in answer
    assert "高原反应" not in answer
    assert "altitude" not in sources

