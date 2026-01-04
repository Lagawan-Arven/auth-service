from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

ENV = os.getenv("ENVIRONMENT","local")

env_file_map = {
    "local":".env.local"
}

env_file = env_file_map.get(ENV)

if env_file:
    env_path = BASE_DIR / env_file
    if env_path.exists():
        load_dotenv(env_path)