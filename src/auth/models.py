from datetime import datetime

from sqlalchemy import Table, Column, Integer, String, TIMESTAMP, Boolean, MetaData
from sqlalchemy_utils import EmailType

from src.database import Base

metadata = MetaData()

user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("email", EmailType, nullable=False),
    Column("username", String(30), nullable=False),
    Column("registered_at", TIMESTAMP, default=datetime.utcnow),
    Column("hashed_password", String(256), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
    extend_existing=True
)


class User(Base):
    __tablename__= 'user'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(EmailType, nullable=False)
    username = Column(String, nullable=False)
    registered_at = Column(TIMESTAMP, default=datetime.utcnow)
    hashed_password: str = Column(String(length=1024), nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    is_superuser: bool = Column(Boolean, default=False, nullable=False)
    is_verified: bool = Column(Boolean, default=False, nullable=False)
