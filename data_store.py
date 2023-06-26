import sqlalchemy
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session


DSN = "postgresql://postgres:1@localhost:5432/vk_db"
engine = sqlalchemy.create_engine(DSN)

metadata = MetaData()
Base = declarative_base()

class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)
    DSN = "postgresql://postgres:1@localhost:5432/vk_db"
    engine = sqlalchemy.create_engine(DSN)

def create_tables(engine):
    Base.metadata.create_all(engine)

create_tables(engine)

"""добавление записи в бд"""
def adder(profile_id, worksheet_id):
    engine = create_engine(DSN)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
        session.add(to_bd)
        session.commit()

"""извлечение записей из БД"""
def filter(profile_id):
    engine = create_engine(DSN)
    v_id = []
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(Viewed.profile_id==profile_id).all()
        for item in from_bd:
            v_id.append(item.worksheet_id)
        return v_id
