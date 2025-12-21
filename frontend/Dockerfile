FROM node:20-slim

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

EXPOSE 5173

# Utilisation de --host pour que Vite accepte les connexions externes au conteneur
CMD ["npm", "run", "dev", "--", "--host"]
