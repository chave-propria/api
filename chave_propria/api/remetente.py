from fastapi import FastAPI

from chave_propria.routers.auth import auth
from chave_propria.routers.cifra_remetente import router
from chave_propria.routers.users import users

remetente = FastAPI()

remetente.include_router(router=router)
remetente.include_router(router=users)
remetente.include_router(router=auth)
