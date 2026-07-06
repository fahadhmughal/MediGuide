from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class MediGuideResponse(BaseModel):
    message_type: Literal["clarifying_question", "specialist_recommendation", "emergency"]
    response_text: str = Field(description="The conversational reply shown to the user")
    clarifying_question: Optional[str] = Field(
        default=None, description="Exactly one follow-up question, never more than one"
    )
    specialists: Optional[List[str]] = Field(default=None)
    appointment_questions: Optional[List[str]] = Field(default=None)
