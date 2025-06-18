from sqlalchemy import Column, Integer, Text, REAL, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Boga_Bucks(Base):
    __tablename__ = "boga_bucks"
    user_id = Column(Integer, primary_key=True)
    boga_bucks = Column(Integer)

class Costs(Base):
    __tablename__ = "costs"
    user_id = Column(Integer, primary_key=True)
    date = Column(Text)
    type = Column(Text)
    cost = Column(REAL)
    user_id_index = Index("user_id_index", user_id)

class Track_Roll(Base):
    __tablename__ = "track_roll"
    user_id = Column(Integer, primary_key=True)
    roll = Column(Integer)
    streak = Column(Integer, default=0)

class Usage(Base):
    __tablename__ = "usage"
    command = Column(Text, primary_key=True)
    count = Column(Integer)

class Track_Wordle(Base):
    __tablename__ = "track_wordle"
    user_id = Column(Integer, primary_key=True)
    checked = Column(Integer)