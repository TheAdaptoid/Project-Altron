"""
This module defines the API router for managing messages. It includes endpoints
for creating, reading, updating, and deleting messages in the database. The
router is configured with a prefix and tags for easy integration with the
FastAPI application.

The module uses SQLModel for database interactions and provides dependencies
for database sessions. HTTP exceptions are raised for error handling when
messages are not found or when request validation fails.
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
    prefix="/messages",
    tags=["messages"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=models.MessageRead)
def create_message(message: models.MessageCreate, db: Session = Depends(get_db)):
    """
    API Endpoint for creating a new message.

    Args:
        message (models.MessageCreate): The data model for creating a message.
        db (Session, optional): The database session used to create the message.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (400): Raised if the message data is invalid.
        HTTPException (500): Raised if there is an error creating the message.

    Returns:
        models.MessageRead: The newly created message.
    """
    logger.info("Creating message...")
    logger.debug("Creating message: %s", message.model_dump())

    try:
        # Retrieve the conversation from the database
        conversation = db.get(models.ConversationTable, message.conversation_id)

        # Verify that the conversation exists
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Create a new message in memory
        try:
            db_message: models.MessageTable = models.MessageTable.model_validate(
                message
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid message data") from e

        # Commit the message to the database
        try:
            db.add(db_message)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error creating message") from e

        # Refresh the database and return the new message
        db.refresh(db_message)
        return db_message

    except HTTPException as e:
        logger.error("Error creating message.  %s", e, exc_info=True)
        raise e from e

    except Exception as e:
        logger.error("Error creating message.  %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Error creating message") from e


@router.get("/", response_model=list[models.MessageRead])
def read_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    API Endpoint for retrieving multiple messages.
    Returns a paginated list of messages.
    Messages are sorted by update time.

    Args:
        conversation_id (int): The ID of the conversation to retrieve messages for.
        skip (int, optional): The number of messages to skip.
            Defaults to 0.
        limit (int, optional): The maximum number of messages to return.
            Defaults to 10.
        db (Session, optional): The database session used to retrieve the messages.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (400): Raised if the skip or limit parameters are invalid.
        HTTPException (404): Raised if the conversation is not found.
        HTTPException (500): Raised if there is an error reading the messages.

    Returns:
        list[models.MessageRead]: The list of messages.
    """
    logger.info("Reading messages...")
    logger.debug("Reading messages: skip=%s, limit=%s", skip, limit)

    try:
        # Validate the request parameters
        if skip < 0 or limit < 0:
            raise HTTPException(
                status_code=400, detail="Invalid skip or limit parameters"
            )

        # Retrieve the conversation from the database
        conversation = db.get(models.ConversationTable, conversation_id)

        # Verify that the conversation exists
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Retrieve the messages from the database
        messages: Sequence[models.MessageTable] = db.exec(
            select(models.MessageTable)
            .where(models.MessageTable.conversation_id == conversation.id)
            .offset(skip)
            .limit(limit)
        ).all()

        # Sort the messages by update time
        messages = sorted(messages, key=lambda m: m.updated_at, reverse=True)

        return messages

    except HTTPException as e:
        logger.error("Error reading messages. %s", e, exc_info=True)
        raise e from e

    except Exception as e:
        logger.error("Error reading messages. %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Error reading messages") from e


@router.get("/{message_id}", response_model=models.MessageRead)
def read_message(message_id: int, db: Session = Depends(get_db)):
    """
    API Endpoint for retrieving a single message.

    Args:
        message_id (int): The ID of the message to retrieve.
        db (Session, optional): The database session used to retrieve the message.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (404): Raised if the message is not found.
        HTTPException (500): Raised if there is an error reading the message.

    Returns:
        models.MessageRead: The retrieved message.
    """
    logger.info("Reading message...")
    logger.debug("Reading message: %s", message_id)

    try:
        # Retrieve the message from the database
        message = db.get(models.MessageTable, message_id)

        # Verify that the message exists
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        return message

    except HTTPException as e:
        logger.error("Error reading message. %s", e, exc_info=True)
        raise e from e

    except Exception as e:
        logger.error("Error reading message. %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Error reading message") from e


@router.patch("/{message_id}", response_model=models.MessageRead)
def update_message(
    message_id: int,
    update_details: models.MessageUpdate,
    db: Session = Depends(get_db),
):
    """
    API Endpoint for updating a message.

    Args:
        message_id (int): The ID of the message to update.
        update_details (models.MessageUpdate): The data model for updating a message.
        db (Session, optional): The database session used to update the message.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (400): Raised if there are no fields to update in the message.
        HTTPException (404): Raised if the message is not found.
        HTTPException (500): Raised if there is an error updating the message.

    Returns:
        models.MessageRead: The updated message.
    """
    logger.info("Updating message...")
    logger.debug("Updating message: %s", message_id)

    try:
        # Retrieve the message from the database
        message_from_db = db.get(models.MessageTable, message_id)

        # Verify that the message exists
        if not message_from_db:
            raise HTTPException(status_code=404, detail="Message not found")

        # Update the message in memory
        message_data: dict[str, Any] = update_details.model_dump(exclude_unset=True)

        # Verify that the update details are valid
        if not message_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update the message in the database
        message_from_db.sqlmodel_update(message_data)

        # Commit the message to the database
        try:
            db.add(message_from_db)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error updating message") from e

        # Refresh the database and return the updated message
        db.refresh(message_from_db)
        return message_from_db

    except HTTPException as e:
        logger.error("Error updating message. %s", e, exc_info=True)
        raise e from e

    except Exception as e:
        logger.error("Error updating message. %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Error updating message") from e


@router.delete("/{message_id}", response_model=dict[str, int | str])
def delete_message(message_id: int, db: Session = Depends(get_db)):
    """
    API Endpoint for deleting a message.

    Args:
        message_id (int): The ID of the message to delete.
        db (Session, optional): The database session used to delete the message.
            Defaults to Depends(get_db).

    Raises:
        HTTPException (404): Raised if the message is not found.
        HTTPException (500): Raised if there is an error deleting the message.

    Returns:
        dict[str, str | int]: A dictionary containing a success message and the deleted message ID.
    """
    logger.info("Deleting message...")
    logger.debug("Deleting message: %s", message_id)

    try:
        # Retrieve the message from the database
        message = db.get(models.MessageTable, message_id)

        # Verify that the message exists
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Delete the message
        try:
            db.delete(message)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Error deleting message") from e

        return {"message_id": message_id, "message": "Message deleted successfully"}

    except HTTPException as e:
        logger.error("Error deleting message.  %s", e, exc_info=True)
        raise e from e

    except Exception as e:
        logger.error("Error deleting message.  %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Error deleting message") from e
