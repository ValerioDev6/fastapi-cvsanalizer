# Proyecto CVQualify AI - Smart Recruitment Automation

## 📋 Descripción del Proyecto

**Resume IA** es una API desarrollada con FastAPI que se encarga de verificar y analizar CVs. El sistema califica los currículums y envía correos electrónicos con los resultados de la evaluación.

## 🚀 Características Principales

- ✅ **Análisis de CVs** en formato PDF
- ✅ **Sistema de calificación** automática
- ✅ **Envío de correos** con resultados
- ✅ **API REST** con FastAPI
- ✅ **Ejecución con Uvicorn**

## 🏗️ Estructura del Proyecto

```
resume-ia/
├── apps/
│   └── bot/
│       ├── bot_router.py      # Rutas de la API
│       ├── bot_schemas.py     # Esquemas Pydantic
│       ├── bot_service.py     # Lógica de negocio
│       └── __pycache__/
├── core/
│   ├── settings.py           # Configuraciones
│   └── __pycache__/
├── main.py                   # Aplicación principal
├── pdf/
│   └── CV-valerio.pdf       # Ejemplo de CV
├── requirements.txt          # Dependencias
└── readme.md               # Documentación
```

## 📦 Dependencias

### requirements.txt
```txt
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0
pdfplumber==0.10.3
emails==0.6.0
jinja2==3.1.2
```

## 🛠️ Instalación y Configuración

### 1. Crear entorno virtual
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables de entorno
Crear archivo `.env`:
```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=tu_email@gmail.com
SENDER_PASSWORD=tu_app_password
ADMIN_EMAIL=admin@empresa.com
```

## 🚀 Ejecución de la Aplicación

### Comando principal:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```



## 📡 Endpoints de la API



### 1. **Analizar CV**
```http
POST /api/v1/analyze-cv
```
**Body:**
```json
{
  "pdf_path": "/ruta/al/cv.pdf",
  "candidate_email": "candidato@email.com",
  "evaluator_email": "evaluador@email.com"
}
```



## 🔧 Funcionalidades del Bot

### Análisis de CV incluye:
- ✅ Extracción de texto con pdfplumber
- ✅ Evaluación de contenido
- ✅ Sistema de puntuación
- ✅ Generación de reportes
- ✅ Envío de correos automáticos

### Ejemplo de flujo:
1. **Subir CV** → PDF se analiza con pdfplumber
2. **Procesar contenido** → Extraer habilidades, experiencia, educación
3. **Calificar** → Asignar puntuación basada en criterios
4. **Enviar resultado** → Correo al candidato/evaluador

## 🌐 URLs de Acceso

- **API Local**: http://localhost:8000
- **Documentación Auto-generada**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc


