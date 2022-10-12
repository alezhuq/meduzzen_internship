from fastapi import APIRouter
import aioredis

router = APIRouter(
    tags=["index"],
)


@router.get("/")
async def read_root():
    redis = await aioredis.from_url('redis://localhost')
    return {"status": "Working"}
