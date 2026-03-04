import os
from dotenv import load_dotenv

load_dotenv()

# JWT
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Google OAuth
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# URLs
BACKEND_URL = "https://quiana-sulphuric-overenthusiastically.ngrok-free.dev"
FRONTEND_URL = "http://localhost:3000"

# Admin user
ADMIN_EMAIL = "avibhatnagar10@gmail.com"