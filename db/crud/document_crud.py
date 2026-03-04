from sqlalchemy.orm import Session
from db.models.document import Document


def create_document(
    db: Session,
    user_id,
    file_name,
    file_type,
    chroma_collection,
    total_chunks
):

    doc = Document(
        user_id=user_id,
        file_name=file_name,
        file_type=file_type,
        chroma_collection=chroma_collection,
        total_chunks=total_chunks
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


def get_user_documents(db: Session, user_id):

    return db.query(Document).filter(Document.user_id == user_id).all()


def get_document(db: Session, document_id):

    return db.query(Document).filter(Document.id == document_id).first()


def delete_document(db: Session, document_id):

    doc = db.query(Document).filter(Document.id == document_id).first()

    if doc:
        db.delete(doc)
        db.commit()

    return doc