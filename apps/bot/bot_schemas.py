from typing import List, Optional

from pydantic import BaseModel, Field


class CVFeedbackResponse(BaseModel):
    """Respuesta del análisis de CV"""

    overall_score: float = Field(..., ge=0, le=10, description="Score general del CV")
    is_valid_candidate: bool = Field(..., description="¿Es desarrollador de software?")
    is_university_graduate: bool = Field(
        ..., description="¿Tiene formación universitaria?"
    )
    is_software_developer: bool = Field(
        ..., description="¿Es desarrollador de software?"
    )
    is_from_peru: bool = Field(..., description="¿Es de Perú?")

    education_score: float = Field(..., ge=0, le=10)
    format_score: float = Field(..., ge=0, le=10)
    experience_score: float = Field(..., ge=0, le=10)
    skills_score: float = Field(..., ge=0, le=10)
    extras_score: float = Field(..., ge=0, le=10)

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
