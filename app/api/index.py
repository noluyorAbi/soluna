from mangum import Mangum
from main import app  # Importiere deine FastAPI-Anwendung aus main.py

handler = Mangum(app)  # Wrappe die FastAPI-App mit Mangum für AWS Lambda (wird von Vercel unterstützt)
