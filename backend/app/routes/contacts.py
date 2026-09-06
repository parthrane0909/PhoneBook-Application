from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..database import get_db
from .. import models
from ..schemas import (
    ContactCreate,
    ContactUpdate,
    ContactResponse,
    ContactListResponse,
    ContactMetricsResponse,
    TagResponse,
    ContactImportRequest,
    ContactImportResponse,
)


router = APIRouter(
    prefix="/contacts",
    tags=["Contacts"]
)


def get_or_create_tags(db: Session, names: list[str]):
    cleaned_names = list(dict.fromkeys(name.strip() for name in names if name.strip()))
    if not cleaned_names:
        return []

    existing = db.query(models.Tag).filter(models.Tag.name.in_(cleaned_names)).all()
    existing_by_name = {tag.name.lower(): tag for tag in existing}
    tags = []

    for name in cleaned_names:
        tag = existing_by_name.get(name.lower())
        if tag is None:
            tag = models.Tag(name=name)
            db.add(tag)
            db.flush()
        tags.append(tag)

    return tags


# CREATE
@router.post("/", response_model=ContactResponse)
def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db)
):
    new_contact = models.Contact(
        name=contact.name,
        phone_number=contact.phone_number,
        email=contact.email,
        address=contact.address
    )
    new_contact.tags = get_or_create_tags(db, contact.tags)

    db.add(new_contact)

    try:
        db.commit()
        db.refresh(new_contact)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Phone number or email already exists"
        )

    return new_contact


# READ ALL + SEARCH + PAGINATION
@router.get("/", response_model=ContactListResponse)
def get_contacts(
    search: str | None = None,
    favorite: bool | None = None,
    tag: str | None = None,
    unlabeled: bool = False,
    recent: bool = False,
    sort: str = Query(
        "name_asc",
        pattern="^(name_asc|name_desc|recently_viewed|recently_added|recently_updated)$",
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(models.Contact)

    if search:
        search_pattern = f"%{search}%"

        query = query.filter(
            (models.Contact.name.ilike(search_pattern)) |
            (models.Contact.phone_number.ilike(search_pattern))
        )

    if favorite is not None:
        query = query.filter(models.Contact.is_favorite == favorite)

    if tag:
        query = query.join(models.Contact.tags).filter(models.Tag.name.ilike(tag))

    if unlabeled:
        query = query.outerjoin(models.Contact.tags).filter(models.Tag.id.is_(None))

    if recent:
        query = query.filter(models.Contact.last_viewed_at.is_not(None))

    if sort == "name_desc":
        query = query.order_by(models.Contact.name.desc())
    elif sort == "recently_viewed":
        query = query.order_by(
            models.Contact.last_viewed_at.desc().nullslast(),
            models.Contact.name.asc(),
        )
    elif sort == "recently_added":
        query = query.order_by(models.Contact.created_at.desc())
    elif sort == "recently_updated":
        query = query.order_by(models.Contact.updated_at.desc())
    else:
        query = query.order_by(models.Contact.name.asc())

    total = query.count()

    offset = (page - 1) * limit

    contacts = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "contacts": contacts,
        "page": page,
        "limit": limit,
        "total": total
    }


@router.get("/metrics", response_model=ContactMetricsResponse)
def get_contact_metrics(db: Session = Depends(get_db)):
    total = db.query(func.count(models.Contact.id)).scalar() or 0
    favorites = (
        db.query(func.count(models.Contact.id))
        .filter(models.Contact.is_favorite.is_(True))
        .scalar()
        or 0
    )
    unlabeled = (
        db.query(func.count(models.Contact.id))
        .outerjoin(models.Contact.tags)
        .filter(models.Tag.id.is_(None))
        .scalar()
        or 0
    )
    recently_added = (
        db.query(func.count(models.Contact.id))
        .filter(models.Contact.created_at >= datetime.utcnow() - timedelta(days=7))
        .scalar()
        or 0
    )

    return {
        "total": total,
        "favorites": favorites,
        "recently_added": recently_added,
        "unlabeled": unlabeled,
    }


@router.get("/tags", response_model=list[TagResponse])
def get_tags(db: Session = Depends(get_db)):
    return db.query(models.Tag).order_by(models.Tag.name.asc()).all()


@router.post("/import", response_model=ContactImportResponse)
def import_contacts(
    payload: ContactImportRequest,
    db: Session = Depends(get_db),
):
    imported = 0
    skipped = 0
    errors = []

    for row_number, contact in enumerate(payload.rows, start=2):
        try:
            with db.begin_nested():
                new_contact = models.Contact(
                    name=contact.name,
                    phone_number=contact.phone_number,
                    email=contact.email,
                    address=contact.address,
                )
                new_contact.tags = get_or_create_tags(db, contact.tags)
                db.add(new_contact)
                db.flush()
            imported += 1
        except IntegrityError:
            skipped += 1
            errors.append({"row": row_number, "reason": "Duplicate phone number or email"})

    db.commit()
    return {"imported": imported, "skipped": skipped, "errors": errors}


# READ ONE
@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    contact = (
        db.query(models.Contact)
        .filter(models.Contact.id == contact_id)
        .first()
    )

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    return contact


# UPDATE
@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(
    contact_id: int,
    contact_data: ContactUpdate,
    db: Session = Depends(get_db)
):
    contact = (
        db.query(models.Contact)
        .filter(models.Contact.id == contact_id)
        .first()
    )

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    update_data = contact_data.model_dump(exclude_unset=True)
    tag_names = update_data.pop("tags", None)

    for field, value in update_data.items():
        setattr(contact, field, value)

    if tag_names is not None:
        contact.tags = get_or_create_tags(db, tag_names)

    try:
        db.commit()
        db.refresh(contact)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Phone number or email already exists"
        )

    return contact


# DELETE
@router.delete("/{contact_id}")
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db)
):
    contact = (
        db.query(models.Contact)
        .filter(models.Contact.id == contact_id)
        .first()
    )

    if contact is None:
        raise HTTPException(
            status_code=404,
            detail="Contact not found"
        )

    db.delete(contact)
    db.commit()

    return {
        "message": "Contact deleted successfully"
    }


@router.patch("/{contact_id}/viewed", response_model=ContactResponse)
def mark_contact_viewed(
    contact_id: int,
    db: Session = Depends(get_db),
):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.last_viewed_at = datetime.utcnow()
    db.commit()
    db.refresh(contact)
    return contact