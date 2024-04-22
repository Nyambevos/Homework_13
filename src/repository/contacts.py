from typing import List

from fastapi import HTTPException
from sqlalchemy import and_
from sqlalchemy.orm import Session

from datetime import date, timedelta

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(skip: int,
                       limit: int,
                       user: User,
                       db: Session) -> List[Contact]:
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    contact = Contact(
        firstname = body.firstname,
        lastname = body.lastname,
        email = body.email,
        phone = body.phone,
        birthday = body.birthday,
        user = user)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        contact.firstname = body.firstname,
        contact.lastname = body.lastname,
        contact.email = body.email,
        contact.phone = body.phone,
        contact.birthday = body.birthday
        db.commit()
    return contact


async def remove_contact(contact_id: int, user: User, db: Session)  -> Contact | None:
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact

async def search_contacts(skip: int,
                       limit: int,
                       firstname: str | None,
                       lastname: str | None,
                       email: str | None,
                       user: User,
                       db: Session) -> List[Contact]:
    filters = []
    if firstname:
        filters.append(Contact.firstname.ilike(f"%{firstname}%"))
    if lastname:
        filters.append(Contact.lastname.ilike(f"%{lastname}%"))
    if email:
        filters.append(Contact.email.ilike(f"%{email}%"))

    if not filters:
        raise HTTPException(status_code=400, detail="Search criteria are not specified")

    return db.query(Contact).filter(and_(*filters, Contact.user_id == user.id)).offset(skip).limit(limit).all()

async def get_upcoming_birthdays(skip: int,
                       limit: int,
                       user: User,
                       db: Session) -> List[Contact]:
    
    today = date.today()
    seven_days_later = today + timedelta(days=7)

    contacts = db.query(Contact).filter(
        and_(Contact.birthday.between(today, seven_days_later), Contact.user_id == user.id)
    ).offset(skip).limit(limit).all()
    return contacts