
from waitress import serve
from app import app, inicializar_db

if __name__ == "__main__":
    inicializar_db()
    serve(app, host="0.0.0.0", port=8000)
