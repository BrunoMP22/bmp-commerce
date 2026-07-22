FROM python:3.13-slim AS runtime
WORKDIR /app

# pyodbc precisa do unixODBC + do driver ODBC da Microsoft para SQL Server instalados no
# SO (o wheel do pyodbc só traz o binding Python — a conexão em si passa pelo driver
# nativo, igual ao pyodbc usado em desenvolvimento no Windows com o "ODBC Driver 17/18
# for SQL Server"). gcc/g++ só são necessários durante a instalação e são removidos
# depois para manter a imagem final enxuta.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl gnupg unixodbc unixodbc-dev gcc g++ \
    && curl -sSL -O https://packages.microsoft.com/config/debian/12/packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get purge -y --auto-remove gcc g++ curl gnupg \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/alembic.ini ./
COPY backend/alembic ./alembic
COPY backend/app ./app

EXPOSE 8080

# Migrations não rodam automaticamente aqui (mesma característica do Program.cs
# original, que só migrava/semeava em Development) — rode `alembic upgrade head`
# manualmente contra o banco do container antes do primeiro uso; ver backend/README.md.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
