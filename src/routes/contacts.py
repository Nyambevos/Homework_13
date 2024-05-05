from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.schemas import ContactModel, ContactResponse
from src.repository import contacts as repository_contacts

router = APIRouter(prefix='/contacts', tags=["contacts"])


@router.get("/", response_model=List[ContactResponse],
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def read_contacts(skip: int = 0,
                        limit: int = 100,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_contacts function returns a list of contacts.
    
    :param skip: int: Skip a number of records
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_contacts(
        skip, limit, current_user, db)
    return contacts

@router.get("/search", response_model=List[ContactResponse])
async def search_contacts(skip: int = 0,
                        limit: int = 100,
                        firstname: str = Query(None, description="Contact name"),
                        lastname:  str = Query(None, description="Contact lastname"),
                        email:  str = Query(None, description="Contact email"),
                        db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The search_contacts function allows you to search for contacts in the database.
    
    :param skip: int: Skip the first n records
    :param limit: int: Limit the number of results returned
    :param firstname: str: Filter the contacts by firstname
    :param description: Document the endpoint
    :param lastname:  str: Filter the contacts by lastname
    :param description: Document the endpoint
    :param email:  str: Filter the contacts by email
    :param description: Document the endpoint
    :param db: Session: Pass the database connection to the function
    :param current_user: User: Get the user that is currently logged in
    :return: A list of contacts, 
    :doc-author: Trelent
    """
    contacts = await repository_contacts.search_contacts(
        skip, limit, firstname, lastname, email, current_user, db)
    
    return contacts

@router.get("/birthdays", response_model=List[ContactResponse])
async def upcoming_birthdays(skip: int = 0,
                        limit: int = 100,
                        db: Session = Depends(get_db),
                        current_user: User = Depends(auth_service.get_current_user)):
    """
    The upcoming_birthdays function returns a list of contacts with upcoming birthdays.
    
    :param skip: int: Skip the first n contacts in the database
    :param limit: int: Limit the number of contacts returned
    :param db: Session: Get a database session
    :param current_user: User: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repository_contacts.get_upcoming_birthdays(skip, limit, current_user, db)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    """
    The read_contact function is used to retrieve a single contact from the database.
    It takes an integer as its first argument, which represents the ID of the contact
    to be retrieved. The function returns a ContactModel object.
    
    :param contact_id: int: Specify the contact id to be read
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user information from the token
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse)
async def create_contact(body: ContactModel,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.
        The function takes a ContactModel object as input, and returns an HTTP response with the newly created contact's data.
        If there is no user logged in, or if the user does not have permission to create contacts, then an HTTP exception will be raised.
    
    :param body: ContactModel: Get the data from the request body
    :param db: Session: Get a database session
    :param current_user: User: Get the current user,
    :return: A contactmodel object
    :doc-author: Trelent
    """
    return await repository_contacts.create_contact(body, current_user, db)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(body: ContactModel,
                         contact_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        It takes an id, a body of type ContactModel and returns the updated contact.
    
    :param body: ContactModel: Get the data from the request body
    :param contact_id: int: Identify the contact that is to be deleted
    :param db: Session: Get the database session
    :param current_user: User: Get the current user
    :return: The updated contact
    :doc-author: Trelent
    """
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    The remove_contact function removes a contact from the database.
    
    :param contact_id: int: Specify the contact to be deleted
    :param db: Session: Pass the database session to the function
    :param current_user: User: Get the user who is currently logged in
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

