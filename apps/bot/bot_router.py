import os

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from apps.bot.bot_schemas import CVFeedbackResponse, ErrorResponse
from apps.bot.bot_service import BotService

router = APIRouter()
service = BotService()


@router.post(
    "/analyze-cv",
    status_code=status.HTTP_200_OK,
    response_model=CVFeedbackResponse,
    responses={
        200: {"model": CVFeedbackResponse},
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def analyze_cv(file: UploadFile = File(...)):
    """
    Analiza CV y envía email SOLO si cumple requisitos

    IMPORTANTE:
    - async def porque usa await para file.read() y send_email()
    - NO guarda archivo en disco
    - Email SOLO si is_valid_candidate == True
    """

    # Validar PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Solo PDF")

    try:
        # 1. Leer EN MEMORIA (await obligatorio)
        pdf_bytes = await file.read()

        # 2. Analizar CV (este método NO es async)
        result = service.analyze_cv_from_bytes(pdf_bytes)

        # 3. SI CUMPLE → Enviar email (await porque send_email SÍ es async)
        email_sent = False
        if result["is_valid_candidate"] and result["candidate_email"]:
            email_sent = await service.send_acceptance_email(
                result["candidate_email"], result["overall_score"]
            )

        # Agregar info de email enviado
        result["email_sent"] = email_sent

        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error: {str(e)}"
        )


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
