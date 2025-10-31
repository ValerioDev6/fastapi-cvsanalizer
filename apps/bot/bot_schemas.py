from typing import List, Optional

from pydantic import BaseModel, Field


class CVFeedbackResponse(BaseModel):
    """Respuesta del análisis de CV"""

    overall_score: float = Field(..., ge=0, le=10)
    is_valid_candidate: bool
    is_university_graduate: bool
    is_software_developer: bool
    is_from_peru: bool
    has_github: bool
    has_portfolio: bool
    years_experience: int = Field(..., ge=0)
    candidate_email: Optional[str] = None
    email_sent: bool = Field(default=False, description="Email enviado SOLO si cumple")

    # Scores
    education_score: float = Field(..., ge=0, le=10)
    format_score: float = Field(..., ge=0, le=10)
    experience_score: float = Field(..., ge=0, le=10)
    skills_score: float = Field(..., ge=0, le=10)
    extras_score: float = Field(..., ge=0, le=10)

    # Feedback
    positive_points: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    critical_errors: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

    education_institution: Optional[str] = None
    professional_summary: str


class ErrorResponse(BaseModel):
    """Respuesta de error"""

    error: str
    detail: Optional[str] = None
