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
     - People limit in group (None for No-limit mode)
     - Security mode: On/Off
     - Password (for Security mode)

    Dynamic parameters:
     - People in chat IRL
     - Favourite messages and their count
     - Message Stream and its count'''

    def __init__(self, name, limit=None, security_mode=False, password=None):
        """Creation of chat."""
        self.name = name
        self.limit = limit
        self.security_mode = security_mode
        self.password = password

        self.people_in_chat = 0
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
        self.sender = sender
        self.ID = ID

        self.favourite = False

    def set_favourite(self):
        """Setup of \'favourites\' label."""
        self.favourite = True
