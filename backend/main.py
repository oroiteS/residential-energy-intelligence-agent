from src import app
from src.config import settings

if __name__ == "__main__":
    app.start(port=settings.PORT, host="127.0.0.1")
    

