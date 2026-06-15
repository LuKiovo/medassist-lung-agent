from medassist_lung_agent.llm.medical_chat import answer_health_question


def test_fever_question_gets_relevant_conversational_answer():
    result = answer_health_question("高烧多少度能吃退烧药", top_k=3)
    answer = result["answer"]
    sources = " ".join(item["source"] for item in result["citations"])
    assert "退烧药" in answer or "退热" in answer
    assert "高原反应" not in answer
    assert "altitude" not in sources


def test_follow_up_answers_are_returned_and_used():
    result = answer_health_question(
        "高烧多少度能吃退烧药",
        top_k=3,
        follow_up_answers={"你的年龄是多少？": "28岁", "症状持续多久了？": "一天"},
    )
    assert result["follow_up_answers"]["你的年龄是多少？"] == "28岁"
    assert "28岁" in result["supplemental_context"]
    assert "一天" in result["answer"] or "一天" in result["supplemental_context"]


def test_emergency_question_returns_resources():
    result = answer_health_question("我现在胸痛还喘不上气怎么办", top_k=2)
    assert result["urgency"] == "emergency"
    assert result["emergency_resources"]["phone"] == "120"
    assert result["emergency_resources"]["human_doctor_url"]
