from databases import DatabaseURL
from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

SECRET_KEY = config("SECRET_KEY", cast=Secret, default="CHANGEME")
POSTGRES_USER = config("POSTGRES_USER", cast=str)
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str, default="db")
POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
POSTGRES_DB = config("POSTGRES_DB", cast=str)
REDIS_HOST = config("REDIS_HOST", cast=str)
SECRET_HASH_KEY = config("SECRET_HASH_KEY", cast=Secret, default="CHANGEME")
DATABASE_URL = config(
    "DATABASE_URL",
    cast=DatabaseURL,
    default=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

REDIS_URL = f"redis://{REDIS_HOST}"

AUTH0_CONFIG = {
    "DOMAIN": config("DOMAIN", cast=str, default="your.domain.com"),
    "API_AUDIENCE": config("API_AUDIENCE", cast=str, default="your.audience.com"),
    "ISSUER": config("ISSUER", cast=str, default="https://your.domain.com/"),
    "ALGORITHMS": config("ALGORITHMS", cast=str, default="RS256"),
}
