# ---- Etapa de Compilación ----
# Usamos una imagen de Node que incluye herramientas de compilación
FROM node:18-slim AS build

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /usr/src/app

# Copiamos los archivos de dependencias y las instalamos
# Usamos 'COPY --chown=node:node' por seguridad, para no usar el usuario root
COPY --chown=node:node package*.json ./
RUN npm ci

# Copiamos el resto del código fuente de la aplicación
COPY --chown=node:node . .

# Compilamos el código TypeScript a JavaScript
RUN npm run build

# ---- Etapa de Producción ----
# Usamos una imagen de Node ligera para producción
FROM node:18-alpine

# Establecemos el directorio de trabajo
WORKDIR /usr/src/app

# Cambiamos al usuario 'node' que es menos privilegiado
USER node

# Copiamos las dependencias de producción desde la etapa de compilación
COPY --chown=node:node --from=build /usr/src/app/node_modules ./node_modules
COPY --chown=node:node package*.json ./

# Copiamos el código JavaScript compilado desde la etapa de compilación
COPY --chown=node:node --from=build /usr/src/app/dist ./dist

# Exponemos el puerto en el que correrá la aplicación
EXPOSE 3000

# El comando para iniciar la aplicación
CMD [ "node", "dist/index.js" ]
