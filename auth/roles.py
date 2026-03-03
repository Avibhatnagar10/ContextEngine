from fastapi import Depends, HTTPException
from auth.dependencies import get_current_user

def require_role(role: str):
    def role_checker(user=Depends(get_current_user)):
        print("ROLE CHECKER CALLED")
        print("USER PAYLOAD:", user)
        if user["role"] != role:
            raise HTTPException(status_code=403, detail="Forbidden")
            
        return user
    return role_checker