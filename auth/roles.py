from fastapi import Depends, HTTPException
from auth.dependencies import get_current_user


def require_roles(*roles):

    def role_checker(user=Depends(get_current_user)):

        print("\n=== ROLE CHECK ===")
        print("Allowed roles:", roles)
        print("User:", user.email)
        print("User role:", user.role)

        if user.role not in roles:
            print("❌ Unauthorized role")
            raise HTTPException(status_code=403, detail="Forbidden")

        print("✅ Role authorized")

        return user

    return role_checker