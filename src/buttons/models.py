from sqlalchemy import Table, Column, Integer, String, Boolean, MetaData, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from src.database import Base
from src.auth.models import user

metadata = MetaData()

buttons = Table(
    "buttons",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(30)),
    Column("status", Boolean),
    Column('owner_id', Integer, ForeignKey(user.c.id), nullable=True),
    Column('token', String(40)),
    extend_existing=True
)


class Button(Base):
    __tablename__ = "buttons"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30))
    status = Column(Boolean)
    owner_id = Column(Integer, ForeignKey('user.id'))
    token = Column(String(40))
    owner: Mapped['User'] = relationship()
