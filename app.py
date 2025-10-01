from enum import Enum
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session
import databases
import sqlalchemy as sa
from pydantic import BaseModel
from models import Wallet
from uuid import UUID

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


def get_session() -> Session:
    return SessionLocal


class OperationType(str, Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class OperationRequest(BaseModel):
    operation_type: OperationType
    amount: float


@app.post('/api/v1/wallets/{wallet_uuid}/operation')
async def wallet_operation(wallet_uuid: UUID, request_data: OperationRequest):
    with get_session() as db:
        try:
            wallet = db.query(Wallet).filter_by(id=str(wallet_uuid)).with_for_update().first()

            if not wallet:
                raise HTTPException(status_code=404, detail="Счет с таким номером не найден")

            if request_data.operation_type.upper() == OperationType.DEPOSIT.value:
                wallet.balance += request_data.amount
            elif request_data.operation_type.upper() == OperationType.DEPOSIT.value:
                if wallet.balance >= request_data.amount:
                    wallet.balance -= request_data.amount
                else:
                    raise HTTPException(status_code=500, detail="Недостаточно средств для проведения операции")

            db.commit()
        except HTTPException as he:
            raise he

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

    return {'message': f"{request_data.operation_type.capitalize()} successful"}


@app.get("/api/v1/wallets/{wallet_uuid}")
async def get_wallet_balance(wallet_uuid: UUID):
    with get_session() as db:
        wallet = db.query(Wallet).filter_by(id=str(wallet_uuid)).first()
        if not wallet:
            raise HTTPException(status_code=404, detail="Счет с таким номером не найден")
        return {"balance": wallet.balance}
