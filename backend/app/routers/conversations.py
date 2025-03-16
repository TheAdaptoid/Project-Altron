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
from typing import Any

# External Libraries
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select

# Internal Libraries
from app import models
from app.database import get_db
from app.logger.logger import logger

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

    Args:
        conversation (models.ConversationCreate): The data model for creating a new conversation.
        db (Session, optional): The database session used to commit the conversation.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (400): Raised if the conversation data is invalid.
        HTTPException (500): Raised if there is an error creating the conversation.

    Returns:
        models.Conversation: The newly created conversation.
    """
    logger.info("Creating conversation...")
    logger.debug("Creating conversation: %s", conversation.model_dump())

    try:
        # Create a new conversation in memory
        try:
            db_conversation: models.ConversationTable = (
                models.ConversationTable.model_validate(conversation)
            )
        except Exception as e:
            raise HTTPException(
                status_code=400, detail="Invalid conversation data"
            ) from e

        # Commit the conversation to the database
        try:
            db.add(db_conversation)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="Error creating conversation"
            ) from e

        # Refresh the database and return the new conversation
        db.refresh(db_conversation)
        return db_conversation

    except HTTPException as e:
        logger.error("Error creating conversation: %s", e)
        raise e from e

    except Exception as e:
        logger.error("Error creating conversation: %s", e)
        raise HTTPException(
            status_code=500, detail="Error creating conversation"
        ) from e


@router.get("/", response_model=list[models.ConversationRead])
def read_conversations(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    API Endpoint for retrieving multiple conversations.
    Returns a paginated list of conversations.
    Conversations are sorted by update time.

    Args:
        skip (int, optional): The number of conversations to skip.
            Defaults to 0.
        limit (int, optional): The maximum number of conversations to return.
            Defaults to 10.
        db (Session, optional): The database session used to retrieve the conversations.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (400): Raised if the skip or limit parameters are invalid.
        HTTPException (500): Raised if there is an error reading the conversations.

    Returns:
        list[models.ConversationRead]: The list of conversations.
    """
    logger.info("Reading conversations...")
    logger.debug("Reading conversations: skip=%s, limit=%s", skip, limit)

    try:
        # Validate the request parameters
        if skip < 0 or limit < 0:
            raise HTTPException(
                status_code=400, detail="Invalid skip or limit parameters"
            )

        # Retrieve the conversations from the database
        conversations: Sequence[models.ConversationTable] = db.exec(
            select(models.ConversationTable).offset(skip).limit(limit)
        ).all()

        # Sort the conversations by update time
        conversations = sorted(conversations, key=lambda c: c.updated_at, reverse=True)

        return conversations

    except HTTPException as e:
        logger.error("Error reading conversations: %s", e)
        raise e from e

    except Exception as e:
        logger.error("Error reading conversations: %s", e)
        raise HTTPException(
            status_code=500, detail="Error reading conversations"
        ) from e


@router.get("/{conversation_id}", response_model=models.ConversationRead)
def read_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    API Endpoint for retrieving a single conversation.

    Args:
        conversation_id (int): The ID of the conversation to retrieve.
        db (Session, optional): The database session used to retrieve the conversation.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (404): Raised if the conversation is not found.
        HTTPException (500): Raised if there is an error reading the conversation.

    Returns:
        models.ConversationRead: The retrieved conversation.
    """
    logger.info("Reading conversation...")
    logger.debug("Reading conversation: %s", conversation_id)

    try:
        # Retrieve the conversation from the database
        conversation = db.get(models.ConversationTable, conversation_id)

        # Verify that the conversation exists
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return conversation

    except HTTPException as e:
        logger.error("Error reading conversation: %s", e)
        raise e from e

    except Exception as e:
        logger.error("Error reading conversation: %s", e)
        raise HTTPException(status_code=500, detail="Error reading conversation") from e


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
        HTTPException (400): Raised if there are no fields to update in the conversation.
        HTTPException (404): Raised if the conversation is not found.
        HTTPException (500): Raised if there is an error updating the conversation.

    Returns:
        models.ConversationRead: The updated conversation.
    """
    logger.info("Updating conversation...")
    logger.debug("Updating conversation: %s", conversation_id)

    try:
        # Retrieve the conversation from the database
        conversation_from_db = db.get(models.ConversationTable, conversation_id)

        # Verify that the conversation exists
        if not conversation_from_db:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Update the conversation in memory
        conversation_data: dict[str, Any] = update_details.model_dump(
            exclude_unset=True
        )

        # Verify that there are fields to update
        if not conversation_data:
            raise HTTPException(
                status_code=400, detail="No fields to update in conversation"
            )

        # Update the conversation in the database
        conversation_from_db.sqlmodel_update(conversation_data)

        # Commit the changes to the database
        try:
            db.add(conversation_from_db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="Error updating conversation"
            ) from e

        # Refresh the database and return the updated conversation
        db.refresh(conversation_from_db)
        return conversation_from_db

    except HTTPException as e:
        logger.error("Error updating conversation: %s", e)
        raise e from e

    except Exception as e:
        logger.error("Error updating conversation: %s", e)
        raise HTTPException(
            status_code=500, detail="Error updating conversation"
        ) from e


@router.delete("/{conversation_id}", response_model=dict[str, int | str])
def delete_conversation(conversation_id: int, db: Session = Depends(get_db)):
    """
    API Endpoint for deleting a conversation.

    Args:
        conversation_id (int): The ID of the conversation to delete.
        db (Session, optional): The database session used to delete the conversation.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (404): Raised if the conversation is not found.
        HTTPException (500): Raised if there is an error deleting the conversation.

    Returns:
        dict[str, str | int]: A dictionary containing a success message and the conversation ID.
    """
    logger.info("Deleting conversation...")
    logger.debug("Deleting conversation: %s", conversation_id)

    try:
        # Retrieve the conversation from the database
        conversation = db.get(models.ConversationTable, conversation_id)

        # Verify that the conversation exists
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Delete the conversation
        try:
            db.delete(conversation)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500, detail="Error deleting conversation"
            ) from e

        return {
            "conversation_id": conversation_id,
            "message": "Conversation deleted successfully",
        }

    except HTTPException as e:
        logger.error("Error deleting conversation: %s", e)
        raise e from e

    except Exception as e:
        logger.error("Error deleting conversation: %s", e)
        raise HTTPException(
            status_code=500, detail="Error deleting conversation"
        ) from e
