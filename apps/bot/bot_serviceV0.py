import json
import os
from typing import Any, Dict

from openai import OpenAI
from pypdf import PdfReader

from core.settings import settings


class BotService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extrae texto del PDF
        """
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error al leer PDF: {str(e)}")

    def analyze_cv_with_openai(self, cv_text: str) -> Dict[str, Any]:
        """
        Envía el CV a OpenAI para análisis profesional
        """

        prompt = f"""
            Eres un reclutador senior de una empresa de tecnología evaluando candidatos para posiciones de desarrollo de software.

            Analiza este CV de forma profesional y objetiva:

            {cv_text}

            INFORMACIÓN A IDENTIFICAR:
            - Nivel de formación: universitaria, técnica, o experiencia autodidacta
            - Perfil: ¿Es desarrollador de software?
            - Ubicación: ¿Es de Perú?

            EVALUACIÓN PROFESIONAL (escala 1-10):

            1. FORMACIÓN (peso 20%):
            - Educación formal o técnica
            - Capacitación relevante
            - Formación continua

            2. PRESENTACIÓN (peso 15%):
            - Estructura clara y profesional
            - Información completa
            - Formato adecuado

            3. EXPERIENCIA PROFESIONAL (peso 35%):
            - Trayectoria en desarrollo de software
            - Proyectos realizados
            - Responsabilidades y logros
            - Años de experiencia

            4. COMPETENCIAS TÉCNICAS (peso 25%):
            - Tecnologías y herramientas
            - Frameworks utilizados
            - Nivel técnico demostrado

            5. ADICIONALES (peso 5%):
            - Portfolio o repositorios
            - Proyectos destacados
            - Información complementaria

            Evalúa de forma objetiva basándote en la experiencia y capacidades demostradas.

            Responde en JSON con esta estructura:
            {{
                "is_university_graduate": boolean,
                "is_software_developer": boolean,
                "is_from_peru": boolean,
                "education_institution": "nombre institución o null",
                "professional_summary": "resumen objetivo del perfil",
                
                "education_score": number,
                "format_score": number,
                "experience_score": number,
                "skills_score": number,
                "extras_score": number,
                
                "positive_points": ["fortaleza 1", "fortaleza 2", "fortaleza 3"],
                "improvements": ["área de mejora 1", "área de mejora 2"],
                "critical_errors": ["solo si hay errores graves"],
                "suggestions": ["recomendación profesional 1", "recomendación 2"]
            }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un reclutador profesional especializado en perfiles de tecnología. Evalúas de forma objetiva y profesional.",
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
        """
        Calcula el score general ponderado
        """
        weights = {
            "education_score": 0.20,
            "format_score": 0.15,
            "experience_score": 0.35,
            "skills_score": 0.25,
            "extras_score": 0.05,
        }

        score = 0.0
        for key, weight in weights.items():
            score += analysis.get(key, 0) * weight

        return round(score, 2)

    def analyze_cv(self, pdf_path: str) -> Dict[str, Any]:
        """
        Método principal que orquesta todo el proceso
        """
        # 1. Extraer texto del PDF
        cv_text = self.extract_text_from_pdf(pdf_path)

        if not cv_text or len(cv_text) < 200:
            raise Exception("El CV es demasiado corto o no se pudo extraer texto")

        # 2. Analizar con OpenAI
        analysis = self.analyze_cv_with_openai(cv_text)

        # 3. Verificar que sea developer
        is_valid_candidate = analysis.get("is_software_developer", False)

        # 4. Calcular score general
        overall_score = self.calculate_overall_score(analysis)

        # 5. Construir respuesta final
        result = {
            "overall_score": overall_score,
            "is_valid_candidate": is_valid_candidate,
            "is_university_graduate": analysis.get("is_university_graduate", False),
            "is_software_developer": analysis.get("is_software_developer", False),
            "is_from_peru": analysis.get("is_from_peru", False),
            "education_institution": analysis.get("education_institution"),
            "professional_summary": analysis.get("professional_summary", ""),
            # Scores
            "education_score": analysis.get("education_score", 0),
            "format_score": analysis.get("format_score", 0),
            "experience_score": analysis.get("experience_score", 0),
            "skills_score": analysis.get("skills_score", 0),
            "extras_score": analysis.get("extras_score", 0),
            # Feedback
            "positive_points": analysis.get("positive_points", []),
            "improvements": analysis.get("improvements", []),
            "critical_errors": analysis.get("critical_errors", []),
            "suggestions": analysis.get("suggestions", []),
        }

        return result
