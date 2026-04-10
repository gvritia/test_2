from fastapi import APIRouter
from models.user import UserCreate

router = APIRouter()

@router.post("/create_user", response_model=UserCreate, response_model_exclude_unset=True)
async def create_user(user: UserCreate):
    return user