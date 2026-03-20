# Acelerador de Microservicios con IA (Node.js)

Este proyecto es un "boilerplate" o plantilla para construir microservicios en Node.js (con TypeScript) que se integran nativamente con servicios de Inteligencia Artificial de AWS.

## Características

- **Framework:** Express.js para la API REST.
- **Lenguaje:** TypeScript.
- **Base de Datos:** PostgreSQL con el ORM Sequelize.
- **Contenerización:** Docker y Docker Compose para un entorno de desarrollo y despliegue consistente.
- **Integración con AWS AI:**
  - **Amazon Rekognition:** Para análisis de imágenes.
  - **Amazon Comprehend:** Para procesamiento de lenguaje natural.
  - **Amazon Polly:** Para síntesis de voz (texto a voz).
- **Pruebas:** Configuración de pruebas con Jest y Supertest.

## Prerrequisitos

- [Node.js](https://nodejs.org/) (versión 18 o superior)
- [Docker](https://www.docker.com/) y [Docker Compose](https://docs.docker.com/compose/)

## Configuración del Entorno

1. Clona este repositorio.
2. Crea un archivo `.env` en la raíz del proyecto, copiando el contenido de `.env.example`.
3. Rellena las variables de entorno en el archivo `.env`. Como mínimo, necesitarás la `DATABASE_URL` y tu región de AWS. Para el desarrollo local, puedes configurar tus credenciales de AWS si no estás usando un rol de IAM.

## Cómo Empezar

### Usando Docker (Recomendado)

Este es el método más sencillo para levantar todo el entorno, incluyendo la base de datos.

```bash
docker-compose up --build
```

La aplicación estará disponible en `http://localhost:3000`.

### Ejecución Local (Sin Docker)

Si prefieres no usar Docker, puedes ejecutar la aplicación localmente. Necesitarás tener una instancia de PostgreSQL corriendo por separado.

1. **Instalar dependencias:**
   ```bash
   npm install
   ```

2. **Ejecutar la aplicación:**
   ```bash
   npm run start
   ```

## Endpoints de la API

Todos los endpoints están prefijados con `/api`.

- **`GET /`**: Endpoint de bienvenida.
- **`POST /api/rekognition/detect-labels`**: Analiza una imagen y detecta etiquetas.
  - **Body:** `multipart/form-data` con un campo `image` que contenga el archivo de imagen.
- **`POST /api/comprehend/detect-sentiment`**: Analiza un texto y determina su sentimiento.
  - **Body (JSON):** `{ "text": "Your text to analyze." }`
- **`POST /api/polly/synthesize-speech`**: Convierte texto a voz y devuelve un archivo de audio MP3.
  - **Body (JSON):** `{ "text": "Your text to synthesize." }`

## Pruebas

Para ejecutar las pruebas unitarias y de integración, usa el siguiente comando:

```bash
npm test
```
