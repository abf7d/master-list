```
POSTGRES_USER=notes_user
POSTGRES_PASSWORD=notes_password
POSTGRES_DB=notes_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
TENANT_ID="<criticalpass>"
AUDIENCE="<criticalpass>"
JWKS_URL="https://criticalplayground.b2clogin.com/criticalplayground.onmicrosoft.com/b2c_1_defaultsigninsignup2/discovery/v2.0/keys"
AZURE_AD_CLIENT_ID="<criticalpass>"
AZURE_AD_CLIENT_SECRET="<criticalpass>"
```

```

when the env variables are not found add env to the docker compose command. In the docker folder run

docker-compose --env-file ../.env --profile init up

the pg_db_init.py file was cached so I used the following and it refreshed properly:
docker-compose --env-file ../.env --profile init build --no-cache
docker-compose --env-file ../.env --profile init up

docker-compose --env-file ../.env --profile init --profile test up

Running tests:
pytest -xvs --capture=tee-sys tests/test_note_service.py
```


