# Utilise Python 3.13 (ou 3.11 si tu préfères)
FROM python:3.13-slim

# Définis le répertoire de travail
WORKDIR /app

# Copie les dépendances
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie tout le code backend
COPY . .

# Expose le port Flask (interne au container)
EXPOSE 5000

# Commande pour lancer Flask avec Gunicorn (production)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "run:app"]
