# AGENT.md - Instrucciones para el Desarrollador de IA (Python)

## 🎯 Objetivo

Actuar como experto en Python y AWS AI para mantener el boilerplate de análisis de riesgos y dependencias.

## 🐍 Reglas de Python

- **Framework:** FastAPI siempre.
- **Tipado:** Usar Type Hints en todas las funciones.
- **Validación:** Pydantic para todos los esquemas de entrada/salida.
- **Estilo:** Seguir PEP 8 y usar nombres de variables descriptivos en inglés.

## ☁️ Integración AWS (Boto3)

- Usar `aioboto3` si se requiere asincronía total con AWS.
- Priorizar **Amazon Bedrock** (modelo Anthropic Claude 3) para análisis de texto complejo.
- Implementar manejo de excepciones para `LimitExceededException` (Cuotas de AWS).

## 🔍 Foco en Análisis de Riesgos

Al generar código para el análisis:

1. Siempre solicitar un esquema JSON de salida al LLM para que sea programático.
2. Separar la "Identificación de Dependencias" (grafos) de la "Detección de Riesgos" (probabilidad/impacto).
