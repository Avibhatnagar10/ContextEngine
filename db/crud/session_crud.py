from sqlalchemy.orm import Session
from datetime import datetime
from db.models.user_session import UserSession


def create_session(
    db: Session,
    user_id,
    refresh_token,
    user_agent=None,
    ip_address=None,
    expires_at=None
):

    user_session = UserSession(
        user_id=user_id,
        refresh_token=refresh_token,
        user_agent=user_agent,
        ip_address=ip_address,
        expires_at=expires_at
    )

    db.add(user_session)
    db.commit()
    db.refresh(user_session)

    return user_session


def get_session_by_token(db: Session, refresh_token: str):

    return (
        db.query(UserSession)
        .filter(UserSession.refresh_token == refresh_token)
        .first()
    )


def get_valid_session(db: Session, refresh_token: str):

    return (
        db.query(UserSession)
        .filter(
            UserSession.refresh_token == refresh_token,
            UserSession.expires_at > datetime.utcnow()
        )
        .first()
    )


def get_user_sessions(db: Session, user_id):

    return (
        db.query(UserSession)
        .filter(UserSession.user_id == user_id)
        .order_by(UserSession.created_at.desc())
        .all()
    )


def delete_session(db: Session, refresh_token: str):

    user_session = (
        db.query(UserSession)
        .filter(UserSession.refresh_token == refresh_token)
        .first()
    )

    if user_session:
        db.delete(user_session)
        db.commit()

    return user_session


def delete_user_sessions(db: Session, user_id):

    db.query(UserSession).filter(
        UserSession.user_id == user_id
    ).delete()

    db.commit()