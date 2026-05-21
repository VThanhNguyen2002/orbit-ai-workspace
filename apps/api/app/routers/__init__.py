from fastapi import APIRouter

from app.routers import ai, auth, health, notes, search, sync, tasks, voice_memos

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(notes.router)
api_router.include_router(tasks.router)
api_router.include_router(voice_memos.router)
api_router.include_router(search.router)
api_router.include_router(sync.router)
api_router.include_router(ai.router)

__all__ = ["api_router"]
