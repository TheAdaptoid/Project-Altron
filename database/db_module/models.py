from abc import ABC, abstractmethod
from datetime import datetime

from db_module.utilities import create_id

ROLES: tuple[str, ...] = ("user", "assistant", "system")


class Role:
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class BaseModel(ABC):
    """
    Abstract base class for all models.
    """

    def __init__(
        self,
        id: int = create_id(),
        created_at: datetime = datetime.now(),
        updated_at: datetime = datetime.now(),
    ) -> None:
        """
        Initializes the model with the given id, created_at and updated_at.

        Args:
            id_ (int): The unique identifier of the model instance. Defaults to a
                newly generated id.
            created_at (datetime): The datetime when the model was created.
                Defaults to the current datetime.
            updated_at (datetime): The datetime when the model was last updated.
                Defaults to the current datetime.
        """
        if not isinstance(id, int):
            raise TypeError("id must be an integer")

        if not isinstance(created_at, datetime):
            raise TypeError("created_at must be a datetime")

        if not isinstance(updated_at, datetime):
            raise TypeError("updated_at must be a datetime")

        self._id = id
        self.__created_at = created_at
        self.__updated_at = updated_at

    @property
    def id(self):
        """
        The unique identifier of the model instance.
        """
        return self._id

    @property
    def created_at(self):
        """
        The datetime when the model was created.
        """
        return self.__created_at

    @property
    def updated_at(self):
        """
        The datetime when the model was last updated.
        """
        return self.__updated_at

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Converts the model to a dictionary representation.

        Returns:
            dict: A dictionary containing the data of the model.
        """
        return {
            "id": self.id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> "BaseModel":
        """
        Creates a new instance of the model from a dictionary representation.

        Args:
            data: A dictionary containing the data to create a new instance of the model.

        Returns:
            A new instance of the model.
        """


class Message(BaseModel):
    """
    A message in a conversation.

    Attributes:
        role (str): The role of the message in the conversation.
        content (str): The content of the message.
        id (int): The unique identifier of the message.
        created_at (datetime): The datetime when the message was created.
        updated_at (datetime): The datetime when the message was last updated.
    """

    def __init__(
        self,
        role: str,
        content: str,
        id: int = create_id(),
        created_at: datetime = datetime.now(),
        updated_at: datetime = datetime.now(),
    ) -> None:
        """
        Initializes a new Message instance.

        Args:
            role: The role of the message in the conversation.
            content: The content of the message.
            id_ (int): The unique identifier of the message. Defaults to a newly
                generated id.
            created_at (datetime): The datetime when the message was created.
                Defaults to the current datetime.
            updated_at (datetime): The datetime when the message was last updated.
                Defaults to the current datetime.

        Raises:
            TypeError: If role is not a string or content is not a string.
            ValueError: If role is not one of the allowed roles or content is empty.
        """
        if not isinstance(role, str):
            raise TypeError("role must be a string")
        if role not in ROLES:
            raise ValueError(f"role must be one of {ROLES}")

        if not isinstance(content, str):
            raise TypeError("content must be a string")
        if not content.strip():
            raise ValueError("content must not be empty")

        super().__init__(id, created_at, updated_at)
        self.__content = content
        self.__role = role

    @property
    def content(self) -> str:
        """
        The content of the message.
        """
        return self.__content

    @content.setter
    def content(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("content must be a string")
        if not value.strip():
            raise ValueError("content must not be empty")
        self.__content = value

    @property
    def role(self) -> str:
        """
        The role of the message in the conversation.
        """
        return self.__role

    def to_dict(self) -> dict:
        """
        Converts the model to a dictionary representation.

        Returns:
            dict: A dictionary containing the data of the model.
        """
        base_dict: dict = super().to_dict()
        base_dict.update(
            {
                "role": self.__role,
                "content": self.__content,
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        """
        Creates a new Message instance from a dictionary representation.

        Args:
            data: A dictionary containing the data to create a new Message instance.

        Returns:
            A new instance of the Message class.
        """

        return cls(**data)


class Thread(BaseModel):
    def __init__(
        self,
        name: str,
        messages: list[Message] | None = None,
        id: int = create_id(),
        created_at: datetime = datetime.now(),
        updated_at: datetime = datetime.now(),
    ) -> None:
        if not isinstance(name, str):
            raise TypeError("name must be a string")
        if not name.strip():
            raise ValueError("name must not be empty")

        if not isinstance(messages, list):
            raise TypeError("messages must be a list")
        if messages and not all(isinstance(message, Message) for message in messages):
            raise TypeError("messages must be a list of Message objects")

        super().__init__(id, created_at, updated_at)
        self.name = name
        self.__messages = messages

    @property
    def messages(self) -> list[Message] | None:
        """
        The list of messages in the thread.
        """
        return self.__messages

    def to_dict(self) -> dict:
        base_dict: dict = super().to_dict()
        base_dict.update(
            {
                "name": self.name,
                "messages": (
                    [message.to_dict() for message in self.__messages]
                    if self.__messages
                    else None
                ),
            }
        )
        return base_dict

    @classmethod
    def from_dict(cls, data: dict) -> "Thread":
        return cls(**data)
