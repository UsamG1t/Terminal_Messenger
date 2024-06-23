'''Description of all objects using in project.'''
import asyncio

from enum import IntEnum


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


class Rights(IntEnum):
    ADMINISTRATOR = 0
    EDITOR = 1
    READER = 2

    def __str__(self):
        if self == Rights.ADMINISTRATOR:
            return 'Administrator'
        if self == Rights.EDITOR:
            return 'Editor'
        if self == Rights.READER:
            return 'Reader'

def arg2Rights(arg):
    match arg:
        case '0':
            return Rights.ADMINISTRATOR
        case '1':
            return Rights.EDITOR
        case '2':
            return Rights.READER
        case 'Administrator':
            return Rights.ADMINISTRATOR
        case 'Editor':
            return Rights.EDITOR
        case 'Reader':
            return Rights.READER


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

        self.users: dict[str, dict[str, (str, Rights)]] = {}  # user_id -> {name, rights}
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
        if limit and limit < len(self.people_in_chat_IRL):
            raise LimitSetupError

        self.limit = limit

    def set_autoright(self, autoright):
        """Setup of autoright

        Available only for the chat administrator

        """
        self.autoright = autoright

    def set_security_mode(self, mode, password = None):
        """Setup of security mode

        Available only for the chat administrator

        """
        self.security_mode = mode
        self.password = hash(password)
    
    def check_password(self, password_to_check):
        """Authorization check."""

        return hash(password_to_check) == self.password

    def check_Rights(self, user, right: Rights):
        """Rights check."""
        chat_user = self.users.setdefault(user._user_id)

        if chat_user is None:
            raise UnvalidChatError

        if right > chat_user['rights']:
            raise NoAccessError

        return True


# set of all chats in TM
TM_chats: dict[str, Chat] = {}


class Message:
    '''Describe parameters of message in chat

    Base characteristics:
     - Text of message
     - Mode of message
     - Style of message
     - Message Sender
     - Message ID

    Dynamic parameters:
     - Reply ID
     - Favourite'''

    def __init__(self, *, text, mode = None, style = None, sender, msg_ID: int, reply_ID = None):
        """Creation of message."""
        self.text = text
        self.mode = mode
        self.style = style
        self._sender = sender
        self._msg_ID = msg_ID


        self.reply_ID = reply_ID
        self.favourite = False

    def set_favourite(self):
        """Setup of \'favourites\' label."""
        self.favourite = True

    def __str__(self):
        res = []
        res.append(f'text: {self.text}')
        res.append(f'mode: {self.mode}')
        res.append(f'style: {self.style}')
        res.append(f'sender: {self._sender}')
        res.append(f'msg_id: {self._msg_ID}')
        res.append(f'reply_id: {self.reply_ID}')
        res.append(f'favourite: {self.favourite}')

        return '\n'.join(res)

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

        self.chats: dict[str, dict[str, (Chat, Rights)]] = {}  # name -> {Chat, rights}
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
        first_time = False

        if self._user_id not in chat.users.keys():
            first_time = True
            chat.users[self._user_id] = {
                'username': self.username,
                'rights': chat.autoright,
                'queue': self.queue,
            }
            self.chats[name] = {
                'chat': chat,
                'rights': chat.autoright
            }
        chat.people_in_chat_IRL.add(self._user_id)
        self.current_chat = chat

        return first_time

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


    def update_chat(self, name, limit: int = -1, autoright: Rights = None, security_mode = None, password = None):
        chat: Chat = TM_chats[name]
        response = []
        try:
            chat.check_Rights(user=self, right=Rights.ADMINISTRATOR)

            if limit != -1:
                chat.set_limit(limit=limit)
                response.append(f'update limit: chat is {(str(limit)+"limited")*(limit is not None) + "Unlimited"*(limit is None)} now')

            if autoright:
                chat.set_autoright(autoright=autoright)
                response.append(f'update autoright: everyone is {str(autoright)} now')
            
            if security_mode:
                chat.set_security_mode(security_mode, password=password)
                response.append(f'update security mode: security mode turn {"on" * security_mode + "off" * (not security_mode)}')

        except TerminalError as e:
            raise e       

        return response


    def add_to_chat(self, user_id, name):
        """Add user to chat

        Available only if you are a chat administrator
        """
        chat: Chat = TM_chats[name]
        user: User = TM_users[user_id]

        try:
            chat.check_Rights(user=self, right=Rights.ADMINISTRATOR)

            chat.users[user._user_id] = {
                'username': user.username,
                'rights': chat.autoright,
                'queue': user.queue
            }
            user.chats[name] = {
                'chat': chat,
                'rights': chat.autoright
            }
        except TerminalError as e:
            raise e       

        return '{} was successfully added to {}'.format(user.username, name)

    def quit_chat(self, name):
        """Quit chat."""
        chat: Chat = TM_chats[name]

        chat.people_in_chat_IRL.discard(self._user_id)
        chat.users.pop(self._user_id)
        self.chats.pop(name)

    def delete_chat(self, name):
        """Delete chat

        Available only if you are a chat administrator
        """
        chat: Chat = TM_chats[name]
        
        users = [TM_users[user] for user in chat.users.keys()]
        for user in users:
            if user.current_chat == chat:
                user.exit_chat()
            user.quit_chat(chat.name)
        TM_chats.pop(chat.name)

    def info_chat(self, name):
        """Take information about chat."""
        chat: Chat = TM_chats[name]

        response: dict[str, any] = {
            'Name': chat.name,
            'Creator': TM_users[chat._creator].username,
            'Participants': [(user['username'], user['rights']) for user in chat.users.values()],
            'Online': [user['username'] for user in chat.users.values() if TLB_names[user['username']] in chat.people_in_chat_IRL]
        }

        return response

    def send(self, *, msg: str, mode: str = None, style: str = None, reply_id: int = None) -> Message:
        """Send message to chat."""
        if self.current_chat is None:
            raise UnvalidChatError()

        message = Message(text=msg, mode=mode, style=style, sender=self, msg_ID=len(self.current_chat.stream), reply_ID=reply_id)
        self.current_chat.stream.append(message)

        return message

    
    def add_to_favourites(self, msg_id: int):
        """Add message to Favourites."""
        if self.current_chat is None:
            raise UnvalidChatError()
        
        msg: Message = self.current_chat.stream[msg_id]
        msg.set_favourite()

        self.current_chat.favourites.append(msg)
    
    def exit_chat(self):
        """Exit current chat."""
        if self.current_chat is None:
            raise UnvalidChatError()
        
        self.current_chat.people_in_chat_IRL.discard(self._user_id)
        self.current_chat = None

# set of all users in TM
TM_users: dict[str, User] = {}
TLB_names: dict[str, str] = {}
