# wallet_api

Для запуска приложения выполнить:
~~~
docker compose up --build -d
~~~

По адресу http://localhost:8000/ доступно 2 метода,

api/v1/wallets/{wallet_uuid}/operation

позволяет пополнить(DEPOSIT) или снять(WITHDRAW) средства со счета

api/v1/wallets/{wallet_uuid}

возвращает текущий баланс счета

После запуска приложения документация доступна тут: 
http://localhost:8000/docs