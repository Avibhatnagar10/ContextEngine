from fastapi import Request, HTTPException
from jose import JWTError
from .jwt_handler import verify_token

async def auth_middleware(request: Request, call_next):
    if request.url.path.startswith("/protected"):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing token")

        token = auth_header.split(" ")[1]

        try:
            payload = verify_token(token)
            request.state.user = payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    response = await call_next(request)
    return response