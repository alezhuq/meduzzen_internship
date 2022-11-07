from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

config = Config("backend/.env")

SECRET_KEY = config("SECRET_KEY", cast=Secret, default="secret")
POSTGRES_USER = config("POSTGRES_USER", cast=str, default="postgres")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret, default="postgres")
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str, default="postgres")
REDIS_HOST = config("REDIS_HOST", cast=str, default="localhost")
SECRET_HASH_KEY = config("SECRET_HASH_KEY", cast=Secret, default="CHANGEME")
DATABASE_URL = config(
    "DATABASE_URL",
    cast=DatabaseURL,
    default=f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

REDIS_URL = f"redis://{REDIS_HOST}"

AUTH0_CONFIG = {
    "DOMAIN": config("DOMAIN", cast=str, default="your.domain.com"),
    "API_AUDIENCE": config("API_AUDIENCE", cast=str, default="your.audience.com"),
    "ISSUER": config("ISSUER", cast=str, default="https://your.domain.com/"),
    "ALGORITHM": config("ALGORITHM", cast=str, default="RS256"),
}
ALG = config("ALG", cast=str,default='HS256'),
SECRET_RSA_KEY = config("SECRET_RSA_KEY", cast=Secret, default="CHANGEME")
