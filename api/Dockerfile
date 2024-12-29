# Verwenden Sie das offizielle Python-Image als Basis
FROM python:3.11-slim

# Setzen Sie Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Setzen Sie das Arbeitsverzeichnis
WORKDIR /app

# Installieren Sie Abhängigkeiten
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren Sie den Anwendungscode
COPY . .

# Exponieren Sie den Port, auf dem FastAPI läuft
EXPOSE 8000

# Befehl zum Ausführen der FastAPI-App mit Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
