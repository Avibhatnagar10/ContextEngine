from fastapi import FastAPI
from auth.oidc import router as auth_router
from api.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# 🔐 Required for OAuth state storage
app.add_middleware(
    SessionMiddleware,
    secret_key="dev-session-secret-key",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://context-engine-ui.vercel.app",
        "https://quiana-sulphuric-overenthusiastically.ngrok-free.dev"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "Context Engine Running"}