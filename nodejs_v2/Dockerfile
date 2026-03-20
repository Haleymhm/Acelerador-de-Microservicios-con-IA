# Etapa de construcción (Builder)
FROM node:20-alpine AS builder

WORKDIR /app

# Copiar configuración de dependencias
COPY package*.json ./

# Instalar TODAS las dependencias (incluyendo devDependencies para compilar TypeScript)
RUN npm ci

# Copiar el código fuente
COPY . .

# Compilar TypeScript a JavaScript (generará la carpeta /dist)
RUN npm run build

# Etapa de producción
FROM node:20-alpine AS runner

WORKDIR /app

# Copiar configuración de dependencias
COPY package*.json ./

# Instalar SOLO las dependencias de producción
RUN npm ci --omit=dev

# Copiar el código compilado de la etapa anterior
COPY --from=builder /app/dist ./dist

# Variables de entorno por defecto
ENV NODE_ENV=production
ENV PORT=3000

# Exponer el puerto
EXPOSE 3000

# Añadir un usuario no root para mayor seguridad (buenas prácticas de Docker)
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001
USER nodejs

# Iniciar la aplicación
CMD ["npm", "start"]
