from fastapi import APIRouter

ping_router = APIRouter(prefix='/ping', tags=["ping"])

@ping_router.get("/")
def ping():
    return {'msg': 'pong'}
