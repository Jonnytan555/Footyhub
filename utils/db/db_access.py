import os
import sqlalchemy as sa


def build_engine(
    server: str | None = None,
    database: str | None = None,
    driver: str | None = None,
    user: str | None = None,
    password: str | None = None,
) -> sa.engine.Engine:
    host     = server   or os.getenv("DB_HOST", "localhost")
    database = database or os.getenv("DB_NAME", "footyhub")
    user     = user     or os.getenv("DB_USER", "")
    password = password or os.getenv("DB_PASSWORD", "")

    return sa.create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}/{database}"
    )


engine = build_engine()
