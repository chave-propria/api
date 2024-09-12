from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chave_propria.routers.auth import auth
from chave_propria.routers.cifra_remetente import router
from chave_propria.routers.contatos import contatos
from chave_propria.routers.message import message
from chave_propria.routers.ping import ping_router
from chave_propria.routers.users import users

remetente = FastAPI()

origins = [
    'http://127.0.0.1/',
    'http://127.0.0.1:8000/',
]


remetente.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

remetente.include_router(router=router)
remetente.include_router(router=users)
remetente.include_router(router=contatos)
remetente.include_router(router=auth)
remetente.include_router(router=ping_router)
remetente.include_router(router=message)
