from fastapi.testclient import TestClient
from app import app
import json

client = TestClient(app)


def test_deposit():
    response = client.post(
        "/api/v1/wallets/fake-wallet-id/operation/",
        data=json.dumps({"operation_type": "DEPOSIT", "amount": 100})
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Deposit successful."


def test_withdraw():
    response = client.post(
        "/api/v1/wallets/fake-wallet-id/operation/",
        data=json.dumps({"operation_type": "WITHDRAW", "amount": 50})
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Withdraw successful."


def test_get_balance():
    response = client.get("/api/v1/wallets/fake-wallet-id")
    assert response.status_code == 200
    assert isinstance(response.json()["balance"], float)
