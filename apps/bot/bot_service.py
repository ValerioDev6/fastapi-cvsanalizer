import json
import re
from io import BytesIO
from typing import Any, Dict, Optional

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from openai import OpenAI
from pypdf import PdfReader

from core.settings import settings


class BotService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # Configurar email
        self.mail_config = ConnectionConfig(
            MAIL_USERNAME=settings.MAILER_EMAIL,
            MAIL_PASSWORD=settings.MAILER_PASSWORD,
            MAIL_FROM=settings.MAILER_EMAIL,
            MAIL_PORT=587,
            MAIL_SERVER=settings.MAILER_SERVICE,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
        self.fast_mail = FastMail(self.mail_config)

    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        """Extrae texto del PDF desde bytes (NO GUARDA)"""
        try:
            pdf_file = BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error al leer PDF: {str(e)}")

    def extract_email_from_text(self, text: str) -> Optional[str]:
        """Extrae email del CV"""
        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else None

    def extract_years_of_experience(self, text: str) -> int:
        """Detecta años de experiencia"""
        years_found = re.findall(r"\b(19|20)\d{2}\b", text)

        if len(years_found) >= 2:
            years = [int(y) for y in years_found]
            start_year = min(years)
            end_year = max(years)
            experience = end_year - start_year
            return max(0, min(experience, 30))

        return 0

    def analyze_cv_with_openai(
        self, cv_text: str, years_experience: int
    ) -> Dict[str, Any]:
        """Analiza CV con OpenAI"""

        prompt = f"""
                Eres un reclutador senior que valora EVIDENCIA REAL sobre títulos.

                Analiza este CV:

                {cv_text}

                AÑOS DE EXPERIENCIA DETECTADOS: {years_experience} años

                CRITERIOS:

                1. FORMACIÓN (15%)
                - Técnica o universitaria (ambas valen)
                - ⚠️ Técnico con GitHub > Universitario sin proyectos

                2. PRESENTACIÓN (10%)
                - Estructura clara

                3. EXPERIENCIA (40%) - MÁS IMPORTANTE
                - Proyectos reales
                - Impacto demostrado

                4. COMPETENCIAS TÉCNICAS (25%)
                - Stack actualizado
                - ⚠️ DEBE tener GitHub

                5. EVIDENCIA (10%)
                - GitHub (+3 puntos)
                - ⚠️ Sin GitHub = -2 puntos

                IMPORTANTE: Todos los scores deben estar entre 0 y 10 (máximo 10).

                Responde en JSON:
                {{
                    "is_university_graduate": boolean,
                    "is_software_developer": boolean,
                    "is_from_peru": boolean,
                    "has_github": boolean,
                    "has_portfolio": boolean,
                    "education_institution": "nombre o null",
                    "professional_summary": "resumen",
                    
                    "education_score": number (0-10, MÁXIMO 10),
                    "format_score": number (0-10, MÁXIMO 10),
                    "experience_score": number (0-10, MÁXIMO 10),
                    "skills_score": number (0-10, MÁXIMO 10),
                    "extras_score": number (0-10, MÁXIMO 10),
                    
                    "positive_points": ["fortaleza 1", "fortaleza 2"],
                    "improvements": ["mejora 1", "mejora 2"],
                    "critical_errors": ["error si existe"],
                    "suggestions": ["recomendación 1"]
                }}
                """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Reclutador que valora EVIDENCIA. GitHub es crítico.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            raise Exception(f"Error al analizar con OpenAI: {str(e)}")

    def calculate_overall_score(self, analysis: Dict[str, Any]) -> float:
        """Calcula score ponderado (máximo 10)"""
        weights = {
            "education_score": 0.15,
            "format_score": 0.10,
            "experience_score": 0.40,
            "skills_score": 0.25,
            "extras_score": 0.10,
        }

        score = 0.0
        for key, weight in weights.items():
            # Asegurar que cada score individual no pase de 10
            individual_score = min(analysis.get(key, 0), 10)
            score += individual_score * weight

        # Penalización sin GitHub
        if not analysis.get("has_github", False):
            score -= 1.5

        # Asegurar que el score final esté entre 0 y 10
        score = max(0, min(score, 10))

        return round(score, 2)

    async def send_acceptance_email(self, to_email: str, score: float) -> bool:
        """Envía email SOLO si cumple requisitos"""
        try:
            subject = "🎉 ¡Felicidades! Fuiste seleccionado"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>¡Felicidades!</h2>
                    <p>Tu perfil ha sido <strong>seleccionado</strong>.</p>
                    <p><strong>Score:</strong> {score}/10</p>
                    <p>Nos contactaremos pronto.</p>
                    <br>
                    <p>Saludos,<br>Equipo de Reclutamiento</p>
                </body>
            </html>
            """

            message = MessageSchema(
                subject=subject, recipients=[to_email], body=body, subtype="html"
            )

            await self.fast_mail.send_message(message)
            return True

        except Exception as e:
            print(f"Error enviando email: {str(e)}")
            return False

    def analyze_cv_from_bytes(self, pdf_bytes: bytes) -> Dict[str, Any]:
        """Analiza CV - NO guarda - SIN async"""
        # 1. Extraer texto
        cv_text = self.extract_text_from_pdf_bytes(pdf_bytes)

        if not cv_text or len(cv_text) < 200:
            raise Exception("CV demasiado corto")

        # 2. Extraer datos
        candidate_email = self.extract_email_from_text(cv_text)
        years_experience = self.extract_years_of_experience(cv_text)

        # 3. Analizar con IA
        analysis = self.analyze_cv_with_openai(cv_text, years_experience)

        # 4. Calcular score
        is_valid_candidate = analysis.get("is_software_developer", False)
        overall_score = self.calculate_overall_score(analysis)

        # 5. Respuesta (sin email todavía)
        return {
            "overall_score": overall_score,
            "is_valid_candidate": is_valid_candidate,
            "is_university_graduate": analysis.get("is_university_graduate", False),
            "is_software_developer": analysis.get("is_software_developer", False),
            "is_from_peru": analysis.get("is_from_peru", False),
            "has_github": analysis.get("has_github", False),
            "has_portfolio": analysis.get("has_portfolio", False),
            "years_experience": years_experience,
            "candidate_email": candidate_email,
            "education_institution": analysis.get("education_institution"),
            "professional_summary": analysis.get("professional_summary", ""),
            "education_score": analysis.get("education_score", 0),
            "format_score": analysis.get("format_score", 0),
            "experience_score": analysis.get("experience_score", 0),
            "skills_score": analysis.get("skills_score", 0),
            "extras_score": analysis.get("extras_score", 0),
            "positive_points": analysis.get("positive_points", []),
            "improvements": analysis.get("improvements", []),
            "critical_errors": analysis.get("critical_errors", []),
            "suggestions": analysis.get("suggestions", []),
        }
