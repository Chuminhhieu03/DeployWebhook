from fastapi import APIRouter
from .meeting import router as meetings_router


router = APIRouter()
router.include_router(meetings_router)
