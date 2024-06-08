'''Description of all objects using in project.'''
import asyncio

from enum import Enum


class TerminalError(Exception):
    """Base class for special Exceptions."""
    pass


class LimitSetupError(TerminalError):
    '''Limit setup error exception.'''

    def __str__(self):
        return """Error during try to setup new limit for chat:
        IRL workload of chat exceeds new limit"""


class NoAccessError(TerminalError):
    '''Access exception.'''

    def __str__(self):
        return """Error during try to do smth without access:
        You don't have the necessary access rights to perform this action"""


class UnvalidChatError(TerminalError):
    '''Access exception.'''

    def __str__(self):
        return """Error during try to do smth with chat where you not in:
        Please join a chat to perform this action"""


class Rights(Enum):
    ADMINISTRATOR = 0
    EDITOR = 2
    READER = 3

    def __init__(self, arg):
        match arg:
            case 0:
                return Rights.ADMINISTRATOR
            case 1:
                return Rights.EDITOR
            case 2:
                return Rights.READER
            case 'Administrator':
                return Rights.ADMINISTRATOR
            case 'Editor':
                return Rights.EDITOR
            case 'Reader':
                return Rights.READER

    def __str__(self):
        if self == Rights.ADMINISTRATOR:
            return 'Administrator'
        if self == Rights.EDITOR:
            return 'Editor'
        if self == Rights.READER:
            return 'Reader'


class Chat:
    '''Describe parameters of text chat

    Base characteristics:
     - Name of chat
     - Chat creator
     - People limit in group (None for No-limit mode)
     - Security mode: On/Off
     - Password (for Security mode)

    Dynamic parameters:
     - List of users in chat and their rights
     - AutoRight (rights of users, who join chat first time)
     - Users in chat IRL
     - Favourite messages and their count
     - Message Stream and its count

    Format of objects in list of users in Chat:
     - user: User
     - rights: Rights
    '''

    def __init__(self, name, creator, limit=None, security_mode=False, password=None, autoright='Editor'):
        """Creation of chat."""
        self.name = name
        self._creator = creator
        self.limit = limit
        self.security_mode = security_mode
        self.password = hash(password)

        self.users = dict()  # user_id -> {name, rights}
        self.autoright = autoright
        self.people_in_chat_IRL = set()
        self.favourites = []
        self.favourites_count = 0
        self.stream = []
        self.stream_count = 0

    def set_limit(self, limit):
        """Setup of people limit

        Available only for the chat administrator

        If count of people online IRL more than new limit,
        return LimitSetupError"""
        if limit < self.people_in_chat:
            return LimitSetupError

        self.limit = limit

    def set_autoright(self, autoright):
        """Setup of autoright

        Available only for the chat administrator

        """
        self.autoright = autoright

    def set_security_mode(self, password):
        """Setup of security mode

        Available only for the chat administrator

        """
        self.security_mode = True
        self.password = password

    def check_password(self, password_to_check):
        """Authorization check."""

        return hash(password_to_check) == self.password

    def check_rights(self, user, right: Rights):
        """Rights check."""
        chat_user = self.users.setdefault(user._user_id)

        if chat_user is None:
            return UnvalidChatError

        if right > chat_user['rights']:
            return NoAccessError

        return True


# set of all chats in TM
TM_chats = dict()


class Message:
    '''Describe parameters of message in chat

    Base characteristics:
     - Text of message
     - Message Sender
     - ID of message in chat

    Dynamic parameters:
     - Favourite'''

    def __init__(self, text, sender, ID):
        """Creation of message."""
        self.text = text
        self._sender = sender
        self.ID = ID

        self.favourite = False

    def set_favourite(self):
        """Setup of \'favourites\' label."""
        self.favourite = True


class User:
    '''Describe parameters of user

    Base characteristics:
     - User's ID (based on your MAC-address of computer)
     - User's name

    Dynamic paremeters:
     - List of chats and user's rights for each chat
     - Current chat

    Format of objects in list of chats in User:
     - user: Chat
     - rights: Rights
    '''

    def __init__(self, user_id, username):
        """Creation of user."""
        self._user_id = user_id
        self.username = username
        self.queue = asyncio.Queue()

        self.chats = dict()  # name -> {Chat, rights}
        self.current_chat = None

    def show_chatlist(self):
        """Show list of user's chats."""
        Avaliable = []
        Hidden = []

        for chat in TM_chats.values():
            right = self.chats[chat.name]['rights'].__str__() if chat.name in self.chats.keys() else ""

            if not chat.security_mode:
                Avaliable.append({'name': chat.name, 'rights': right})
            else:
                Hidden.append({'name': chat.name, 'rights': right})

        return (Avaliable, Hidden)

    def open_chat(self, name):
        """Open existing chat."""
        chat: Chat = TM_chats[name]

        if self._user_id not in chat.users.keys():
            chat.users[self._user_id] = {
                'username': self.username,
                'rights': chat.autoright,
                'queue': self.queue
            }
        chat.people_in_chat_IRL.add(self._user_id)

    def create_chat(
            self,
            name: str,
            limit: int | None = None,
            security_mode: bool = False,
            password=None,
            autoright: Rights = Rights.EDITOR
    ):
        """Create new chat."""
        new_chat = Chat(
            name=name,
            creator=self._user_id,
            limit=limit,
            security_mode=security_mode,
            password=password,
            autoright=autoright
        )

        new_chat.users[self._user_id] = {
            'username': self.username,
            'rights': Rights.ADMINISTRATOR,
            'queue': self.queue
        }
        self.chats[name] = {
            'chat': new_chat,
            'rights': Rights.ADMINISTRATOR
        }
        TM_chats[name] = new_chat

        return {
            'name': name,
            'limit': limit if limit else "Unlimited",
            'security_mode': security_mode,
            'autoright': autoright
        }

    def add_to_chat(self, user_id, name):
        """Add user to chat

        Available only if you are a chat administrator
        """
        chat: Chat = TM_chats[name]
        user: User = TM_users[user_id]

        chat.users[user._user_id] = {
            'username': user.username,
            'rights': chat.autoright,
            'queue': user.queue
        }

    def quit_chat(self, name):
        """Quit chat."""
        chat: Chat = TM_chats[name]

        chat.people_in_chat_IRL.discard(self._user_id)
        chat.users.pop(self._user_id)

    def delete_chat(self, name):
        """Delete chat

        Available only if you are a chat administrator
        """
        chat: Chat = TM_chats[name]

        for user in chat.users:
            user.quit_chat(chat.name)
        TM_chats.pop(chat.name)

    def info_chat(self, name):
        """Take information about chat."""
        pass


# set of all users in TM
TM_users = dict()
