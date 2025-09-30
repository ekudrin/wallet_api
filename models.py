from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Float

Base = declarative_base()

class Wallet(Base):
    __tablename__ = 'wallet'
    id = Column(String(length=36), primary_key=True)
    balance = Column(Float(), nullable=False)