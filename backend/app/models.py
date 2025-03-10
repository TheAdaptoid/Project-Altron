"""
This module defines the SQLModel data models for conversations (and other models once implemented).
It provides base, table, and specific models for creating, reading,
and updating records in the database.
"""

from datetime import datetime

# External Libraries
from sqlmodel import Field, SQLModel


class ConversationBase(SQLModel):
    """
    Base class for conversations.
    """

    title: str = Field(default="New Conversation", nullable=False, index=True)


class ConversationTable(ConversationBase, table=True):
    """
    Database table for conversations.
    \nFields:
        id: int
        title: str
        created_at: datetime
        updated_at: datetime
    """

    id: int | None = Field(default=None, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.now, nullable=False)


class ConversationCreate(ConversationBase):
    """
    Data model for creating a new conversation.
    \nFields:
        title: str
    """


class ConversationRead(ConversationBase):
    """
    Data model for retrieving a conversation.
    \nFields:
        id: int
        title: str
        created_at: datetime
        updated_at: datetime
    """

    # Read only values
    id: int
    created_at: datetime
    updated_at: datetime


class ConversationUpdate(ConversationBase):
    """
    Data model for updating a conversation.
    \nFields:
        title: str
    """
