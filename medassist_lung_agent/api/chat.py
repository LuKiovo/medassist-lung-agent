from pydantic import BaseModel, Field
from fastapi import APIRouter

from medassist_lung_agent.llm.medical_chat import answer_health_question


router = APIRouter()


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    top_k: int = Field(4, ge=1, le=8)


@router.post("")
def chat(req: ChatRequest):
    return answer_health_question(req.question, top_k=req.top_k)

