from pydantic import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

DB_URL = os.environ.get('DB_URL')
SECRET_AUTH = os.environ.get('SECRET_AUTH')
DOCS_URL = os.environ.get('DOCS_URL')
TITLE = os.environ.get('TITLE')


class FastApiSettings(BaseSettings):
    docs_url: str | None = DOCS_URL
    title: str = TITLE