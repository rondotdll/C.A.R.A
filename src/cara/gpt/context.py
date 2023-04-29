from discord import User, ClientUser, TextChannel
from discord.message import Message

import attr


@attr.define(auto_attribs=True)
class ContextMessage:
    content: str
    is_assistant: bool
    message: Message | None = None

    def __str__(self):
        return self.content


@attr.define(auto_attribs=True)
class Context:
    """
    Represents the context of a Discord conversation with CARA.
    """

    assistant_user: ClientUser
    for_user: User
    for_channel: TextChannel
    frame_size: int = 5

    __context: list[ContextMessage] = attr.ib(factory=list)

    def openai_messages(self) -> list:
        return [
            {
                "role": "assistant" if msg.is_assistant else "user",
                "content": msg.content
                if msg.is_assistant
                else f"[{msg.message.author.display_name or msg.message.author.name}]: {msg.content}",
            }
            for msg in self.__context
        ]

    def add_assistant_msg(self, msg: str):
        if len(self.__context) == self.frame_size:
            del self.__context[0]
        self.__context.append(ContextMessage(msg, True))

    def latest(self) -> ContextMessage:
        """
        Returns the latest message in the context.
        :return: a tuple of (is_assistant, message_content)
        """
        return self.__context[-1]

    def __getitem__(self, key: int):
        return self.__context[key]

    def __iadd__(self, other):
        if not isinstance(other, Message):
            raise TypeError(
                f"unsupported operand type(s) for +=: 'ContextManager' and '{type(other)}'"
            )

        if other.channel != self.for_channel:
            raise ValueError(
                f"cannot add message from channel {other.channel} to context for channel {self.for_channel}"
            )

        if other.author != self.for_user:
            raise ValueError(
                f"cannot add message from user {other.author} to context for user {self.for_user}"
            )

        # remove the first message if the context stack is full...
        if len(self.__context) == self.frame_size:
            del self.__context[0]

        self.__context.append(
            ContextMessage(
                content=other.content,
                is_assistant=other.author == self.assistant_user,
                message=other,
            )
        )

        return self

    def __len__(self):
        return len(self.__context)


@attr.define(auto_attribs=True)
class ContextCollection:
    assistant_user: ClientUser
    frame_size: int = 5
    __contexts: dict[tuple[User, TextChannel], Context] = attr.ib(factory=dict)

    def __getitem__(self, key: tuple[User, TextChannel]):
        if not isinstance(key, tuple):
            raise TypeError(
                f"unsupported operand type(s) for []: 'ContextCollection' and '{type(key)}'"
            )

        # if the context doesn't exist for the user and channel, create it.
        if key not in self.__contexts:
            new = Context(
                assistant_user=self.assistant_user,
                for_user=key[0],
                for_channel=key[1],
                frame_size=self.frame_size,
            )
            self.__contexts[key[0], key[1]] = new
            return new

        return self.__contexts[key[0], key[1]]
