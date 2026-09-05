from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from .database import Base, engine
from . import models
from .routes.contacts import router as contacts_router
from . import models, schemas
from .database import get_db


app = FastAPI(
    title="Phonebook API",
    description="REST API for managing contacts",
    version="1.0.0"
)


# Allow our Vue frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": "Phonebook API is running"
    }


# Register contact routes
app.include_router(contacts_router)

@app.patch("/contacts/{contact_id}/favorite")
def update_favorite(
    contact_id: int,
    favorite: schemas.FavoriteUpdate,
    db: Session = Depends(get_db),
):
    contact = (
        db.query(models.Contact)
        .filter(models.Contact.id == contact_id)
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=404,
            detail="Contact not found",
        )

    contact.is_favorite = favorite.is_favorite

    db.commit()
    db.refresh(contact)

    return contact