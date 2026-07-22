"""Configuração da aplicação (equivalente a appsettings.json + appsettings.Development.json)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Connection string no formato SQLAlchemy (pyodbc). Default aponta para o mesmo
    # SQL Server local usado pelo backend .NET anterior.
    database_url: str = (
        "mssql+pyodbc://localhost/BMPCommerceDb"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&TrustServerCertificate=yes"
    )

    jwt_key: str = "bmp-commerce-local-dev-signing-key-nao-usar-em-producao-2026"
    jwt_issuer: str = "BMPCommerce"
    jwt_audience: str = "BMPCommerceClients"
    jwt_expiry_minutes: int = 480

    environment: str = "Development"

    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


settings = Settings()
