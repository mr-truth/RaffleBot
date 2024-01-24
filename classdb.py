from sqlalchemy import Column, MetaData, Table, create_engine
from sqlalchemy.types import Integer, Text

engine = create_engine("sqlite:///test.db", pool_pre_ping=True)
db = engine.connect()

raffles = Table( 'raffles', MetaData(),
    Column('id', Integer, primary_key=True, unique=True, autoincrement=True, nullable=False),
    Column('name', Text),
    Column('text', Text),
    Column('time', Text),
    Column('ucount', Integer),
    Column('wintext', Text),
    Column('fromm', Integer)
)

usersraf = Table( 'usersraf', MetaData(),
    Column('id', Integer, primary_key=True, unique=True, autoincrement=True, nullable=False),
    Column('nicktele', Text, nullable=False),
    Column('idtele', Integer, nullable=False),
    Column('textid', Text, nullable=False),
    Column('idraf', Integer, nullable=False)
)