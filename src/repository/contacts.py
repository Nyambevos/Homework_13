from typing import List

from fastapi import HTTPException
from sqlalchemy import and_, extract
from sqlalchemy.orm import Session

from datetime import date, timedelta

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(skip: int,
                       limit: int,
                       user: User,
                       db: Session) -> List[Contact]:
    """
    The get_contacts function returns a list of contacts for the user.
    
    :param skip: int: Skip a number of records in the database
    :param limit: int: Limit the number of contacts returned
    :param user: User: Get the user_id of the user that is logged in
    :param db: Session: Access the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    return db.query(Contact).filter(Contact.user_id == user.id).offset(skip).limit(limit).all()


async def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    The get_contact function takes in a contact_id and user, and returns the contact with that id.
    It also checks to make sure that the user is allowed to access this contact.
    
    :param contact_id: int: Get the contact with a specific id
    :param user: User: Check if the user is authorized to access this contact
    :param db: Session: Pass the database session to the function
    :return: A contact object
    :doc-author: Trelent
    """
    return db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()


async def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    The create_contact function creates a new contact in the database.
    
    :param body: ContactModel: Specify the type of data that is expected to be passed into the function
    :param user: User: Get the user information from the database
    :param db: Session: Access the database
    :return: The newly created contact
    :doc-author: Trelent
    """
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
    """
    The update_contact function updates a contact in the database.
        Args:
            contact_id (int): The id of the contact to update.
            body (ContactModel): The new values for the Contact object.  This is a Pydantic model, so it will be validated before being passed into this function.
            user (User): A User object representing who is making this request and whose contacts are being updated/deleted/etc...
    
    :param contact_id: int: Identify the contact to be updated
    :param body: ContactModel: Specify the type of data that will be passed to the function
    :param user: User: Check if the user is authorized to update the contact
    :param db: Session: Access the database
    :return: A contact object
    :doc-author: Trelent
    """
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
    """
    The remove_contact function removes a contact from the database.
        Args:
            contact_id (int): The id of the contact to be removed.
            user (User): The user who is removing the contact. This is used for security purposes, so that users can only remove their own contacts and not other users' contacts. 
            db (Session): A session object which allows us to interact with our database in order to delete a row from it.
    
    :param contact_id: int: Specify the id of the contact to be deleted
    :param user: User: Get the user_id of the contact to be deleted
    :param db: Session: Pass the database session to the function
    :return: The contact that was removed
    :doc-author: Trelent
    """
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
    """
    The search_contacts function searches for contacts in the database.
    
    :param skip: int: Skip the first n contacts
    :param limit: int: Limit the number of results returned
    :param firstname: str | None: Specify that the firstname parameter is optional
    :param lastname: str | None: Filter the contacts by lastname
    :param email: str | None: Filter contacts by email
    :param user: User: Get the current user from the request
    :param db: Session: Access the database
    :return: A list of contact objects
    :doc-author: Trelent
    """
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
    
    """
    The get_upcoming_birthdays function returns a list of contacts with birthdays in the next seven days.
    
    :param skip: int: Skip a certain number of contacts
    :param limit: int: Limit the number of results returned
    :param user: User: Get the user id of the current user
    :param db: Session: Pass the database session to the function
    :return: A list of contacts whose birthdays are in the next seven days
    :doc-author: Trelent
    """
    today = date.today()
    seven_days_later = today + timedelta(days=7)

    # contacts = db.query(Contact).filter(
    #     and_(Contact.birthday.between(today, seven_days_later), Contact.user_id == user.id)
    # ).offset(skip).limit(limit).all()

    results = db.query(Contact).filter(
        and_(
            and_(
                extract('month', Contact.birthday) == today.month,
                extract('day', Contact.birthday) >= today.day),
            and_(
                extract('month', Contact.birthday) == seven_days_later.month,
                extract('day', Contact.birthday) <= seven_days_later.day)
            )
        ).all()

    return results




