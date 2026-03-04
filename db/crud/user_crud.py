from sqlalchemy.orm import Session
from db.models.user import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id):
    return db.query(User).filter(User.id == user_id).first()


def create_user(
    db: Session,
    name: str,
    email: str,
    password_hash: str,
    role: str = "user"
):
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role,           
        is_verified=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user