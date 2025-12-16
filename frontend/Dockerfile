# Stage 1 : Build du frontend
FROM node:20-alpine AS builder

WORKDIR /app

# Copie les fichiers de config npm
COPY package*.json ./

# Installe les dépendances
RUN npm install

# Copie tout le code frontend
COPY . .

# Build le projet (génère le dossier dist/)
RUN npm run build

# Stage 2 : Serveur Nginx pour servir le frontend
FROM nginx:alpine

# Copie le build depuis le stage précédent
COPY --from=builder /app/dist /usr/share/nginx/html

# Copie la config Nginx personnalisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose le port 80 (interne au container)
EXPOSE 80

# Démarre Nginx
CMD ["nginx", "-g", "daemon off;"]
