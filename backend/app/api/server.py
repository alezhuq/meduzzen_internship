import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.api.routes import user_endpoints, user_auth

from app.core import tasks

app = FastAPI()

app.include_router(user_endpoints.router)
app.include_router(user_auth.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", tasks.create_start_app_handler(app))
app.add_event_handler("shutdown", tasks.create_stop_app_handler(app))

if __name__ == "__main__":
    uvicorn.run("server:app", reload=True, host='0.0.0.0', port=8000)
