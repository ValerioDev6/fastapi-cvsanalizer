import os

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from apps.bot.bot_schemas import CVFeedbackResponse, ErrorResponse
from apps.bot.bot_service import BotService

router = APIRouter()
service = BotService()


@router.post(
    "/feedback-cv",
    status_code=status.HTTP_200_OK,
    response_model=CVFeedbackResponse,
    responses={
        200: {"model": CVFeedbackResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def analyze_cv():
    """
    Analiza el CV desde la carpeta /pdf

    Evalúa de forma profesional y objetiva el perfil del candidato.

    Returns:
        - Score general (0-10)
        - Validación de perfil developer
        - Feedback detallado por categorías
        - Fortalezas identificadas
        - Áreas de mejora
        - Sugerencias profesionales
    """
    try:
        pdf_path = os.path.join("pdf", "CV-valerio.pdf")

        if not os.path.exists(pdf_path):
            raise HTTPException(
                status_code=404, detail="CV no encontrado en /pdf/CV-valerio.pdf"
            )
        result = service.analyze_cv(pdf_path)

        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al analizar CV: {str(e)}",
        )
