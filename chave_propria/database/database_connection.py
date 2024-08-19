from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from chave_propria.settings.Settings import Settings

engine = create_engine(Settings().DATABASE_URL)


def database_session():  # pragma: no cover
    with Session(engine) as session:
        yield session
