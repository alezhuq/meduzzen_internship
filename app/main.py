import uvicorn
from fastapi import FastAPI
from routers import index

app = FastAPI()

app.include_router(index.router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host='0.0.0.0', port=8000)