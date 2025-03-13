"""
This module defines the API router for managing conversations. It includes
endpoints for creating, reading, updating, and deleting conversations in the
database. The router is configured with a prefix and tags for easy integration
with the FastAPI application.

The module uses SQLModel for database interactions and provides dependencies
for database sessions. HTTP exceptions are raised for error handling when
conversations are not found or when request validation fails.
"""

# Standard Libraries
from collections.abc import Sequence

# External Libraries
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

# Internal Libraries
from app import models
from app.database import get_db

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=models.ConversationRead)
def create_conversation(
    conversation: models.ConversationCreate, db: Session = Depends(get_db)
):
    """
    API Endpoint for creating a new conversation.
    Takes a ConversationCreate pydantic model as input.
    This model will contain only a title.
    The rest of the fields will be auto-generated.

    Args:
        conversation (models.ConversationCreate): The data model for creating a new conversation.
        db (Session, optional): The database session used to commit the conversation.
            Defaults to Depends(get_db).

    Returns:
        models.Conversation: The newly created conversation.
    """
    # Create a new conversation in memory
    db_conversation: models.ConversationTable = models.ConversationTable.model_validate(
        conversation
    )

    # Commit the conversation to the database
    db.add(db_conversation)
    db.commit()

    # Refresh the database and return the new conversation
    db.refresh(db_conversation)
    return db_conversation


@router.get("/", response_model=list[models.ConversationRead])
def read_conversations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    API Endpoint for retrieving multiple conversations.
    Returns a paginated list of conversations.

    Args:
        skip (int, optional): The number of conversations to skip.
            Defaults to 0.
        limit (int, optional): The maximum number of conversations to return.
            Defaults to 10.
        db (Session, optional): The database session used to retrieve the conversations.
            Defaults to Depends(get_db).

    Returns:
        list[models.Conversation]: The list of conversations.
    """
    conversations: Sequence[models.ConversationTable] = db.exec(select(models.ConversationTable).offset(skip).limit(limit)).all()
    
    # Sort the conversations by update time
    conversations = sorted(conversations, key=lambda c: c.updated_at, reverse=True)
    
    return conversations


@router.get("/{conversation_id}", response_model=models.ConversationRead)
def read_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    API Endpoint for retrieving a single conversation.

    Args:
        conversation_id (int): The ID of the conversation to retrieve.
        db (Session, optional): The database session used to retrieve the conversation.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: Raised if the conversation is not found.

    Returns:
        models.Conversation: The retrieved conversation.
    """
    # Retrieve the conversation from the database
    conversation = db.get(models.ConversationTable, conversation_id)

    # Verify that the conversation exists
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return conversation


@router.patch("/{conversation_id}", response_model=models.ConversationRead)
def update_conversation(
    conversation_id: int,
    update_details: models.ConversationUpdate,
    db: Session = Depends(get_db),
):
    """
    API Endpoint for updating a conversation.

    Args:
        conversation_id (int): The ID of the conversation to update.
        update_details (models.ConversationUpdate): The data model for updating a conversation.
        db (Session, optional): The database session used to update the conversation.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: Raised if the conversation is not found.

    Returns:
        models.Conversation: The updated conversation.
    """
    # Retrieve the conversation from the database
    conversation_from_db = db.get(models.ConversationTable, conversation_id)

    # Verify that the conversation exists
    if not conversation_from_db:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Update the conversation in memory
    conversation_data: dict = update_details.model_dump(exclude_unset=True)
    conversation_from_db.sqlmodel_update(conversation_data)

    # Commit the changes to the database
    db.add(conversation_from_db)
    db.commit()

    # Refresh the database and return the updated conversation
    db.refresh(conversation_from_db)
    return conversation_from_db


@router.delete("/{conversation_id}", response_model=dict[str, int | str])
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    API Endpoint for deleting a conversation.

    Args:
        conversation_id (int): The ID of the conversation to delete.
        db (Session, optional): The database session used to delete the conversation.
            Defaults to Depends(get_db).

    Raises:
        HTTPException: Raised if the conversation is not found.

    Returns:
        dict[str, str]: A dictionary containing a success message.
    """
    # Retrieve the conversation from the database
    conversation = db.get(models.ConversationTable, conversation_id)

    # Verify that the conversation exists
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Delete the conversation
    db.delete(conversation)

    # Commit the changes and return a success message
    db.commit()
    return {
        "conversation_id": conversation_id,
        "message": "Conversation deleted successfully",
    }
