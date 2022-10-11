from fastapi import APIRouter

router = APIRouter(
    tags=["index"],
)


@router.get("/")
def read_root():
    return {"status": "Working"}
