import os
from pathlib import Path
from dotenv import load_dotenv

current_path = Path(__file__).resolve()
base_dir = current_path.parent.parent
env_path = base_dir / ".env" 

load_dotenv(dotenv_path=env_path)

class Settings:
    BASE_DIR: Path = base_dir
    
    ENV: str = os.getenv("APP_ENV", "production")
    PORT: int = int(os.getenv("PORT", 8080))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default_secret")

settings = Settings()

