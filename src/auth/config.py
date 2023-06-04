from pydantic import BaseModel

from src.config import SECRET_AUTH


class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_AUTH
    authjwt_header_type: str = 'Bearer'
