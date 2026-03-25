# 🚀 Guía de Configuración AWS para el Acelerador de Microservicios Node.js

Bienvenido. Como Arquitecto de Soluciones Cloud, he preparado esta guía paso a paso para que puedas configurar todos los servicios de AWS necesarios para este proyecto.

Imagina que AWS (Amazon Web Services) es como un centro comercial gigante lleno de tiendas (servicios). Tu proyecto Node.js es tu asistente personal, pero para que este asistente pueda entrar a las tiendas y pedir cosas (como generar texto, analizar fotos o hablar), primero necesita una **identificación válida** y que nosotros abramos las puertas de esas tiendas.

---

## 🛑 PASO 1: El Portero del Centro Comercial (AWS IAM)

Antes de usar cualquier IA, necesitamos crear una "credencial de empleado" para que tu código de Node.js pueda demostrarle a AWS quién es y qué tiene permitido hacer. Esto se hace con un servicio llamado **IAM** (Identity and Access Management).

1. **Entra a la consola de AWS** y busca el servicio llamado **IAM**.
2. Ve a la sección **"Usuarios" (Users)** a la izquierda y haz clic en **"Crear usuario"**.
3. Ponle un nombre fácil de reconocer, por ejemplo: `mi-app-ia-nodejs`. No le des acceso a la consola web (no lo necesita, es un programa, no un humano).
4. **Asignar permisos:** AWS te preguntará qué puede hacer este usuario. Selecciona **"Adjuntar políticas directamente"**.
5. Busca y selecciona (marcándolas con un check) las siguientes políticas (estas son las llaves a las tiendas):
   - `AmazonBedrockFullAccess` (Para que pueda generar texto).
   - `AmazonRekognitionFullAccess` (Para que pueda ver y entender imágenes).
   - `AmazonTextractFullAccess` (Para que pueda leer documentos).
   - `AmazonPollyFullAccess` (Para que pueda hablar).
6. Haz clic en siguiente y crea el usuario.
7. **Crear las llaves secretas:** Entra al usuario que acabas de crear, ve a la pestaña "Credenciales de seguridad" y haz clic en **"Crear clave de acceso" (Access Key)**.
8. AWS te dará dos códigos larguísimos: un **Access Key ID** (tu usuario) y un **Secret Access Key** (tu contraseña). **¡Cópialos y guárdalos en un lugar seguro!** Es la única vez que verás el secreto.

---

## 🧠 PASO 2: La Mente Maestra (Amazon Bedrock)

Bedrock es el servicio de AWS donde viven los "cerebros" de inteligencia artificial más avanzados (como Claude de Anthropic, que funciona parecido a ChatGPT). 

*Importante:* AWS tiene estos modelos apagados por seguridad para cuentas nuevas, tienes que pedir que te los enciendan.

1. Busca el servicio **Amazon Bedrock** en la consola de AWS.
2. Asegúrate de estar en una región que soporte Bedrock, como `us-east-1` (N. Virginia), que es la que usa tu proyecto por defecto.
3. En el menú de la izquierda (abajo del todo), haz clic en **"Acceso a modelos" (Model access)**.
4. Verás una tabla con muchos modelos. Haz clic en el botón naranja **"Administrar acceso al modelo" (Manage model access)** arriba a la derecha.
5. Marca la casilla de los modelos que vayas a usar. Según tu código, estás usando la familia **Claude 3** de Anthropic. Marca los modelos de Claude. 
   *(Nota: Si es la primera vez que usas modelos de Anthropic, puede que AWS te pida llenar un pequeño formulario con los casos de uso, solo pon que es para desarrollo y pruebas estudiantiles).*
6. Baja al final y guarda los cambios. ¡Listo! En unos minutos los modelos estarán en estado "Access granted" (Acceso concedido).

---

## 👁️ PASO 3: Los Ojos Digitales (Amazon Rekognition)

Este servicio es el que le permite a tu proyecto recibir una imagen y decir "aquí hay un perro, un auto, o una persona feliz".

**Configuración necesaria:** ¡Ninguna extra! 
A diferencia de Bedrock, Rekognition funciona "sacándolo de la caja". Al haberle dado los permisos (`AmazonRekognitionFullAccess`) a tu usuario en el PASO 1, tu código ya está listo para enviarle fotos y recibir el análisis.

---

## 📖 PASO 4: El Lector de Documentos (Amazon Textract)

Textract es un escáner inteligente. Si le pasas la foto de una factura o un documento, te devuelve el texto perfectamente escrito e incluso estructurado en tablas.

**Configuración necesaria:** ¡Tampoco requiere configuración extra en la consola!
Con el permiso `AmazonTextractFullAccess` del PASO 1, tu aplicación ya puede extraer texto directamente.

---

## 🗣️ PASO 5: La Voz del Sistema (Amazon Polly)

Polly convierte el texto en un audio con voces humanas y naturales.

**Configuración necesaria:** Ninguna configuración extra en la consola. 
Igual que los dos anteriores, funcionará automáticamente gracias a las llaves maestras creadas en el PASO 1.

---

## 🔌 PASO FINAL: Conectar tu código con AWS

Ahora que AWS está listo y tienes tus llaves de acceso del PASO 1, debemos decirle a tu proyecto de Node.js dónde están esas llaves para que pueda entrar.

1. Abre tu proyecto en tu editor de código.
2. Busca el archivo llamado `.env`. Si no existe, crea uno copiando el esqueleto que menciona tu archivo `README.md`.
3. Llénalo con la información de la región y las llaves que obtuviste en el PASO 1, reemplazando lo que está después del signo de igual `=`:

```env
# Server Configuration
PORT=3000
NODE_ENV=development

# AWS Configuration (N. Virginia es us-east-1)
AWS_REGION=us-east-1

# Tus llaves del PASO 1 van aquí:
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

¡Y eso es todo! 🚀
Tu arquitectura Node.js está lista. Al correr `npm run dev`, los "Adaptadores" de tu proyecto tomarán estas variables `.env`, se autenticarán con AWS, y tu API estará lista para probar todos los servicios. Si hay algún error de permisos o configuración, revisa siempre la consola de tu terminal.
