"""
This module defines the SQLModel data models for conversations (and other models once implemented).
It provides base, table, and specific models for creating, reading,
and updating records in the database.
"""

# Standard Libraries
from datetime import datetime
from enum import Enum

# External Libraries
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, DateTime


class Role(str, Enum):
    """
    Enum for roles in a conversation.

    Values:
        USER - The role of a user.
        ASSISTANT - The role of an assistant.
        SYSTEM - The role of the system.
    """

    user = "user"
    assistant = "assistant"
    system = "system"


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
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
        ),
    )

    # Relationships
    messages: list["MessageTable"] = Relationship(
        back_populates="conversation",
        cascade_delete=True,
    )


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


class MessageBase(SQLModel):
    """
    Base class for messages.
    """

    text: str = Field(default="", nullable=True)


class MessageTable(MessageBase, table=True):
    """
    Database table for messages.
    \nFields:
        id: int
        conversation_id: int
        role: str
        text: str
        created_at: datetime
        updated_at: datetime
    """

    id: int | None = Field(default=None, primary_key=True, index=True)
    role: Role = Field(default="user", nullable=False)
    created_at: datetime = Field(default_factory=datetime.now, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.now,
        sa_column=Column(
            DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
        ),
    )

    # Relationships
    conversation_id: int | None = Field(
        foreign_key="conversationtable.id", nullable=False
    )
    conversation: ConversationTable = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    """
    Data model for creating a new message.
    \nFields:
        conversation_id: int
        role: str
        text: str
    """

    conversation_id: int
    role: Role


class MessageRead(MessageBase):
    """
    Data model for retrieving a message.
    \nFields:
        id: int
        conversation_id: int
        role: str
        text: str
        created_at: datetime
        updated_at: datetime
    """

    id: int
    conversation_id: int
    role: Role
    # text: str
    created_at: datetime
    updated_at: datetime


class MessageUpdate(MessageBase):
    """
    Data model for updating a message.
    \nFields:
        text: str
    """
