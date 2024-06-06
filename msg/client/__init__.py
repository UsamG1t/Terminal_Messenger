"""Main logic of client program."""
import cmd
import readline
import socket
import threading


class clientCmd(cmd.Cmd):
    """Cmd class."""

    prompt = ">>"

    def __init__(self, socket, *args, **kwargs):
        """Create client workspace."""
        self.socket = socket
        return super().__init__(*args, **kwargs)

    def do_EOF(self, args):
        """Stop game."""
        return 1

    def emptyline(self):
        """Hide previous commands."""
        return

    def do_show_chatlist(self, args):
        """Shows a list of chats available to the client."""

    def do_open_chat(self, args):
        """Opens chat."""

    def do_create_chat(self, args):
        """Create chat."""

    def do_quit_chat(self, args):
        """Quit chat, leaving chat without acces for the client."""

    def do_delete_chat(self, args):
        """Delete chat."""

    def do_info_chat(self, args):
        """Shows information about the chat: number and names of participants."""

    def do_send(self, args):
        """Send the message."""

    def do_add_to_favorites(self, args):
        """Add message to favorites."""

    def do_reply(self, args):
        """Reply to the message."""

    def do_exit(self, args):
        """Exit chat."""


def msg_receiver(client):
    """Function for receiving messages."""
    while res := client.socket.recv(1024).rstrip().decode():
        print(f"\n{res}\n{client.prompt}{readline.get_line_buffer()}", end="", flush=True)


def start_client(username, host="localhost", port=1337):
    """Start client."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        client = clientCmd(s)
        handler = threading.Thread(target=msg_receiver, args=(client,))
        handler.start()
        client.cmdloop()
