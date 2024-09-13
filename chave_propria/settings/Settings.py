import logging

from pydantic_settings import BaseSettings

FORMAT = '%(message)s'

logging.basicConfig(level='NOTSET', format=FORMAT, datefmt='[%X]')

log = logging.getLogger(__name__)


class Settings(BaseSettings):
    BLOCO_BYTES: int = 8  # Quantidade de bytes dentro do bloco
    IDEA_ROUNDS: int = 12  # Quantidades de rodadas do algoritmo IDEA
    KEYS_PATH: str = '/opt/cript/projeto/'
    DATABASE_URL: str = 'sqlite:///database.db'

    SECRET_KEY: str = 'c819963052b5b294811bbdfe46651e9d0699eb8935c8faee43725d9239463847a487908f468f04b95f3935545c4d2d85238c677e62259779a05a3605dc8b7755ae8b8fcc1c594bd690786bb64289b663b13a7ed2800aa2fd30e0dffa4e4d602608c0b92faa84eb153fc740eb3975a47c59617954becffc6e006ff95eaebd89899c32227893c2b789c6650b7e56bb09dd5b7b5264fd8cd30d94c43f7b1e15d4ee214ce167a3e1d23fda4f4f5b7bd413fbb670bf6592020810d0a94bd3cdc24f597cd176703c87ecb17e3b836a5049d2d578b8468b8651'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
