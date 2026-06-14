from medassist_lung_agent.agent.router import plan_consultation


def test_agent_marks_chest_pain_as_emergency():
    decision = plan_consultation("我现在胸痛还喘不上气怎么办")
    assert decision.intent in {"respiratory", "xray_consult", "general_health"}
    assert decision.urgency == "emergency"
    assert decision.red_flags
    assert any("急诊" in item or "急救" in item for item in decision.next_actions)


def test_agent_classifies_gastroenteritis():
    decision = plan_consultation("肠胃炎了要吃什么药")
    assert decision.intent in {"gi", "medication"}
    assert decision.urgency == "routine"

