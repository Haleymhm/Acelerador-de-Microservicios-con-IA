# Roadmap de Desarrollo e Implementación (Python)

## Fase 1: Estructura Base y Configuración (Días 1-3)

- [x] **1.1 Setup de Proyecto:** Inicializar entorno virtual (Poetry o venv) y configurar `pyproject.toml`.
- [x] **1.2 Arquitectura de Carpetas:** Implementar estructura: `/app/api`, `/app/core` (config), `/app/services` (IA), `/app/models` (Pydantic).
- [x] **1.3 Cliente AWS Boto3:** Crear un provider centralizado para Bedrock y S3 con manejo de sesiones y reintentos.

## Fase 2: Implementación del Motor de IA (Días 4-8)

- [x] **2.1 Módulo de Extracción (Textract):** Crear servicio para convertir documentos (PDF/Imágenes) en texto plano analizable.
- [x] **2.2 Prompt Engineering para Riesgos:** Diseñar y probar prompts en Bedrock para identificar "Riesgos" y "Dependencias" a partir de texto desestructurado.
- [x] **2.3 Lógica de Análisis:** Implementar el servicio `RiskAnalyzerService` que orqueste la llamada al LLM y parsee la respuesta JSON.
- [x] **2.4 Almacenamiento de Resultados:** Guardar los análisis en una base de datos (PostgreSQL/DynamoDB) para auditoría.

## Fase 3: API y Automatización (Días 9-12)

- [x] **3.1 Endpoints de FastAPI:** Crear rutas para subir documentos y consultar el estado del análisis de riesgos.
- [x] **3.2 Procesamiento en Background:** Configurar tareas asíncronas para que el usuario no espere a que la IA termine el análisis.
- [x] **3.3 Documentación Swagger:** Personalizar la documentación automática de FastAPI para incluir ejemplos de payloads de riesgo.

## Fase 4: Despliegue y Validación (Días 13-15)

- [x] **4.1 Dockerización:** Crear una imagen `slim-python` optimizada para despliegue rápido.
- [x] **4.2 IaC (Infraestructura):** Escribir los manifiestos de Terraform para los permisos de Bedrock.
- [x] **4.3 Test de Stress:** Simular el análisis de un proyecto de "gran escala" (ej. 50 documentos simultáneos) y optimizar cuotas de AWS.
