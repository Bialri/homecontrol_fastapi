from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Time, Interval, Boolean
from sqlalchemy.orm import relationship, Mapped
from src.auth.models import user
from src.database import Base

metadata = MetaData()

devices = Table(
    'devices',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', String(50)),
    extend_existing=True
)

actions = Table(
    'actions',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', String(100)),
    Column('device_type', Integer, ForeignKey('devices.id'), nullable=True),
    extend_existing=True
)

script_actions = Table(
    'script_actions',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('device_id', Integer),
    Column('latency', Interval),
    Column('action_id', Integer, ForeignKey('actions.id'), nullable=True),
    extend_existing=True
)

scripts = Table(
    'scripts',
    metadata,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('name', String(100)),
    Column('time', Time),
    Column('single_execution', Boolean),
    Column('owner_id', Integer, ForeignKey(user.c.id), nullable=True),
    extend_existing=True
)

actions_association_table = Table(
    'actions_association_table',
    metadata,
    Column('script_action_id', Integer, ForeignKey('script_actions.id'), primary_key=True),
    Column('script_id', Integer, ForeignKey('scripts.id'), primary_key=True),
    extend_existing=True
)


class Device(Base):
    __tablename__ = 'devices'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(50))


class Action(Base):
    __tablename__ = 'actions'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))
    device_type = Column(Integer, ForeignKey('devices.id'))
    device: Mapped['Device'] = relationship()


class ActionsAssociation(Base):
    __tablename__ = 'actions_association_table'
    __table_args__ = {'extend_existing': True}
    script_action_id = Column(Integer, ForeignKey(script_actions.c.id), primary_key=True)
    script_id = Column(Integer, ForeignKey(scripts.c.id), primary_key=True)


class ScriptAction(Base):
    __tablename__ = 'script_actions'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, autoincrement=True, primary_key=True)
    device_id = Column(Integer)
    latency = Column(Interval)
    action_id = Column(Integer, ForeignKey('actions.id'))
    action: Mapped['Action'] = relationship()


class Script(Base):
    __tablename__ = 'scripts'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(100))
    time = Column(Time)
    single_execution = Column(Boolean)
    owner_id = Column(Integer, ForeignKey('user.id'))
    owner: Mapped['User'] = relationship(backref='script')
    actions: Mapped[list['ScriptAction']] = relationship(secondary='actions_association_table',
                                                         primaryjoin=
                                                         'Script.id == ActionsAssociation.script_id',
                                                         secondaryjoin=
                                                         'ActionsAssociation.script_action_id == ScriptAction.id')
