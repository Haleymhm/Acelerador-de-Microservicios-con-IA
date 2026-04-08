# Análisis de Requerimientos: Acelerador de Microservicios con IA (Python)

## 1. Objetivo

Desarrollar un boilerplate en Python para microservicios que utilicen IA de AWS para automatizar la detección de dependencias y riesgos en proyectos de gran escala mediante procesamiento de lenguaje natural (NLP).

## 2. Requerimientos Funcionales (RF)

| ID | Requerimiento | Descripción |
| :--- | :--- | :--- |
| **RF-01** | **Ingesta de Documentación** | Capacidad de procesar archivos de texto, Markdown, PDFs y exportaciones de Jira/Confluence. |
| **RF-02** | **Análisis de Dependencias** | Uso de Amazon Bedrock (Claude 3/Llama 3) para identificar relaciones lógicas entre componentes mencionadas en texto. |
| **RF-03** | **Detección de Riesgos** | Clasificación de riesgos (técnicos, de cronograma o recursos) mediante análisis de sentimiento y extracción de entidades. |
| **RF-04** | **Integración AWS Nativa** | Uso de Boto3 para interactuar con Amazon Bedrock, Textract (para PDFs) y S3 (almacenamiento). |
| **RF-05** | **API REST** | Exposición de funcionalidades mediante endpoints asíncronos para manejo de tareas pesadas. |

## 3. Requerimientos No Funcionales (RNF)

* **Asincronía:** El análisis de grandes volúmenes de texto debe ser no bloqueante (usando Celery o FastAPI Background Tasks).
* **Seguridad:** Implementación de roles de IAM y cifrado de datos en tránsito (TLS 1.3).
* **Escalabilidad:** Preparado para ejecutarse en AWS Lambda o AWS App Runner (contenedores).
* **Calidad de Código:** Tipado estricto con Pydantic y validación con MyPy.

## 4. Stack Tecnológico

* **Framework:** FastAPI (por su alto rendimiento y soporte asíncrono).
* **IA/ML:** Boto3 (AWS SDK), LangChain (Orquestación de LLMs).
* **Validación de Datos:** Pydantic v2.
* **Infraestructura:** Terraform o AWS SAM.
