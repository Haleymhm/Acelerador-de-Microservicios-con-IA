# 🚀 Acelerador de Microservicios con Inteligencia Artificial (IA) en AWS

Este proyecto es un **Boilerplate** para construir microservicios en **Node.js** con integraciones nativas a los servicios de Inteligencia Artificial de Amazon Web Services (AWS SDK v3).

Está diseñado siguiendo los principios de la **Arquitectura Limpia (Clean Architecture)** y utiliza tipado estricto con **TypeScript**.

## 🏗️ Arquitectura y Estructura

El código está estructurado en capas para garantizar escalabilidad, facilidad de pruebas y bajo acoplamiento con la infraestructura de AWS.

- **`src/domain`**: Contiene las interfaces (puertos) para definir los contratos de los servicios de IA (ej. `ILlmService`, `IVisionService`).
- **`src/application`**: Contiene los casos de uso (`Use Cases`) que implementan la lógica de negocio orquestando los servicios del dominio.
- **`src/infrastructure/aws`**: Aloja los adaptadores de AWS. Aquí es donde los SDKs v3 se comunican con internet (AWS Bedrock, Rekognition, etc.).
- **`src/interfaces/http`**: Controladores web y rutas manejadas vía Express.
- **`src/shared`**: Utilidades comunes transversales al sistema, como un `ConfigService` estricto (Zod), manejadores globales de errores y un sistema de *logging* (Winston).

## 🔌 Servicios de IA de AWS Soportados

Este boilerplate incluye adaptadores nativos para los siguientes servicios:
1. **AWS Bedrock (Generación de Texto / Chat)**: Integrado con modelos como Claude 3 (`AwsBedrockService.ts`).
2. **AWS Rekognition (Computer Vision)**: Análisis de imágenes, detección de objetos y rostros potenciales (`AwsRekognitionService.ts`).
3. **AWS Textract (OCR y Documentos)**: Extracción de texto desde imágenes/PDF de forma síncrona o asíncrona (`AwsTextractService.ts`).
4. **AWS Polly (Audio / TTS)**: Síntesis nativa de texto a voz neuronal (`AwsPollyService.ts`).

## ⚙️ Requisitos Previos

- **Node.js**: v20 o superior (LTS recomendado).
- **AWS CLI**: Para manejar tus credenciales locales si vas a probar de forma local.
- **Docker** y **Docker Compose** (Opcional si prefieres correr todo en contenedores).

## 📥 Instalación local

1. Instala las dependencias:
   ```bash
   npm install
   ```
2. Crea una copia de las variables de entorno:
   Renombra o edita tu propio archivo `.env` en la raíz (tienes un esqueleto listo).
   ```env
   # Server Configuration
   PORT=3000
   NODE_ENV=development

   # AWS Configuration
   AWS_REGION=us-east-1
   
   # Opcional si NO usas un rol IAM en instacia / SSO Profile en tu máquina
   # AWS_ACCESS_KEY_ID=tu_llave
   # AWS_SECRET_ACCESS_KEY=tu_secreto
   ```

## 💻 Scripts Disponibles

- `npm run dev`: Inicia el servidor de desarrollo usando `ts-node-dev` (Hot-reload activado).
- `npm run build`: Compila la aplicación estricta en TypeScript a la carpeta `./dist`.
- `npm start`: Levanta la aplicación usando el código en modo producción (`node dist/index.js`).
- `npm run test`: Ejecuta la suite de pruebas unitarias implementada de inicio en **Jest**.

## 🐳 Despliegue con Docker

El proyecto viene provisto de un `Dockerfile` optimizado (*multi-stage*) y un archivo `docker-compose.yml`.

1. **Construye y levanta el contenedor**:
   ```bash
   docker-compose up --build
   ```

La imagen ignorará tu código de desarrollo y compilará la aplicación desde cero generando su propia carpeta estática `/dist`. *(Nota: `docker-compose.yml` montará la carpeta oculta `~/.aws` por default para que tu contenedor lea tus permisos de la máquina Host)*.

## 🎯 Endpoints de Prueba

Una vez se levanta la aplicación (en `http://localhost:3000`), cuentas por defecto con dos Endpoints de prueba:

### 1. Healthcheck
- **Ruta:** `GET /health`
- **Descripción:** Verifica que el servidor está escuchando.

### 2. Generación de Texto con Claude (Bedrock)
- **Ruta:** `POST /api/v1/ai/generate-text`
- **Body JSON:**
  ```json
  {
    "prompt": "Escribe un pequeño saludo introduciendo este acelerador de microservicios"
  }
  ```

### 3. Análisis de Imagen con Vision (Rekognition)
- **Ruta:** `POST /api/v1/ai/analyze-image`
- **Body `form-data`**:
  - `image`: [Archivo adjunto de la imagen]
  - `detectFaces`: (Opcional) `true` o `false`.

---

> **Nota para Desarrolladores:**
> Todo error operacional controlado es capturado por un Middleware global, respondiendo correctamente un JSON estandarizado conforme la clase madre `AppError`. Asegúrate de lanzar errores bajo esta clase para tener trazas útiles en el logger o modificarlo a necesidad en `src/shared/errors/AppError.ts`.
