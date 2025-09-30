import os

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import sqlalchemy as sa
import databases
from pydantic import BaseModel
from models import Wallet
from typing import Optional
from uuid import UUID
from contextlib import asynccontextmanager


DATABASE_URL = "postgresql://postgres:password@db:5432/wallet_db"
database = databases.Database(DATABASE_URL)
metadata = sa.MetaData()
engine = sa.create_engine(DATABASE_URL)
sessionmaker = sa.orm.sessionmaker(bind=engine)
SessionLocal = sessionmaker()



app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

class OperationRequest(BaseModel):
    operation_type: str
    amount: float

def get_session() -> Session:
    return SessionLocal

@app.post('/api/v1/wallets/{wallet_uuid}/operation')
async def wallet_operation(wallet_uuid: UUID, request_data: OperationRequest):
    with get_session() as db:
        try:
            wallet = db.query(Wallet).filter_by(id=str(wallet_uuid)).with_for_update().first()

            if not wallet:
                raise HTTPException(status_code=404, detail="Счет с таким номером не найден")

            if request_data.operation_type.upper() == 'DEPOSIT':
                wallet.balance += request_data.amount
            elif request_data.operation_type.upper() == 'WITHDRAW':
                if wallet.balance >= request_data.amount:
                    wallet.balance -= request_data.amount
                else:
                    raise HTTPException(status_code=404, detail="Недостаточно средств для проведения операции")

            db.commit()

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail= "Ошибка при попытке провести транзакцию")

    return {'message': f"{request_data.operation_type.capitalize()} successful"}

@app.get("/api/v1/wallets/{wallet_uuid}")
async def get_wallet_balance(wallet_uuid: UUID):
    with get_session() as db:
        wallet = db.query(Wallet).filter_by(id=str(wallet_uuid)).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Счет с таким номером не найден")
        return {"balance": wallet.balance}
