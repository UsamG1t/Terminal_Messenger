'''Description of all objects using in project.'''


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
     - rights: str; one of ['Administrator', 'Editor', 'Reader']
    '''

    def __init__(self, name, creator, limit=None, security_mode=False, password=None, autoright='Editor'):
        """Creation of chat."""
        self.name = name
        self._creator = creator
        self.limit = limit
        self.security_mode = security_mode
        self.password = password

        self.users = []
        self.autoright = autoright
        self.people_in_chat_IRL = []
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

    def set_security_mode(self, password):
        """Setup of security mode

        Available only for the chat administrator

        """
        self.security_mode = True
        self.password = password


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
     - rights: str; one of ['Administrator', 'Editor', 'Reader']
    
    '''

    def __init__(self, user_id, user_name):
        """Creation of user."""
        self._user_id = user_id
        self.user_name = user_name

        self.chats = []
        self.current_chat = None

    def show_chatlist(self):
        """Show list of user's chats."""
        return [(chat.name, rights) for chat, rights in self.chats]
    
    def open_chat(self, name):
        """Open existing chat."""
        pass

    def create_chat(self, name, limit, security_mode, password, autoright):
        """Create new chat."""
        pass
    
    def quit_chat(self, name):
        """Quit chat."""
        pass
    
    def delete_chat(self, name):
        """Delete chat
        
        Available only if you are a chat administrator
        """
        pass

    def info_chat(self, name):
        """Take information about chat."""
        pass