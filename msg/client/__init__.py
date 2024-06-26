"""Main logic of client program."""
import cmd
import readline
import socket
import threading
import shlex
import webbrowser
import os
from ..common import *


class clientCmd(cmd.Cmd):
    """Cmd class."""

    prompt = ">>"

    def __init__(self, socket, *args, **kwargs):
        """Create client workspace."""
        self.s = socket
        return super().__init__(*args, **kwargs)

    def do_EOF(self, args):
        """Stop game."""
        return 1

    def emptyline(self):
        """Hide previous commands."""
        return

    def do_show_chatlist(self, args):
        """Show a list of chats available to the client."""
        self.s.sendall("show_chatlist\n".encode())

    def do_open_chat(self, args):
        """Open chat."""
        cmd = shlex.split(args)
        if len(cmd) == 1:
            msg = f"open_chat {cmd[0]}\n"
        elif len(cmd) == 2:
            msg = f"open_chat {cmd[0]} {cmd[1]}\n"
        elif len(cmd) == 0:
            print("You need write chat name")
            return
        else:
            print("Invalid arguments")
            return
        self.s.sendall(msg.encode())

    def do_create_chat(self, args):
        """Create chat."""
        msg = f"create_chat {args}\n"
        self.s.sendall(msg.encode())

    def do_update_chat(self, args):
        """Update chat settings."""
        msg = f"update_chat {args}\n"
        self.s.sendall(msg.encode())

    def do_add_to_chat(self, args):
        """Add someone in the chat."""
        cmd = shlex.split(args)
        if len(cmd) < 2:
            print("you need to write username and chat name")
            return
        if len(cmd) > 2:
            print("Invalid arguments")
            return
        msg = f"add_to_chat {cmd[0]} {cmd[1]}\n"
        self.s.sendall(msg.encode())

    def do_quit_chat(self, args):
        """Quit chat, leaving chat without acces for the client."""
        cmd = shlex.split(args)
        if len(cmd) != 1:
            print("Invalid arguments")
            return
        msg = f"quit_chat {cmd[0]}\n"
        self.s.sendall(msg.encode())

    def do_delete_chat(self, args):
        """Delete chat."""
        cmd = shlex.split(args)
        if len(cmd) != 1:
            print("Invalid arguments")
            return
        msg = f"delete_chat {cmd[0]}\n"
        self.s.sendall(msg.encode())

    def do_info_chat(self, args):
        """Show information about the chat: number and names of participants."""
        cmd = shlex.split(args)
        if len(cmd) != 1:
            print("Invalid arguments")
            return
        msg = f"info_chat {cmd[0]}\n"
        self.s.sendall(msg.encode())

    def do_send(self, args):
        """Send the message."""
        msg = f"send {args}\n"
        self.s.sendall(msg.encode())

    def do_add_to_favourites(self, args):
        """Add message to favorites."""
        cmd = shlex.split(args)
        if len(cmd) < 1:
            print("you need to write message id")
            return
        if len(cmd) > 1:
            print("Invalid arguments")
            return
        msg = f"add_to_favourites {cmd[0]}\n"
        self.s.sendall(msg.encode())

    def do_reply(self, args):
        """Reply to the message."""
        msg = f"reply {args}\n"
        self.s.sendall(msg.encode())

    def do_exit(self, args):
        """Exit chat."""
        cmd = shlex.split(args)
        if len(cmd) != 0:
            print("Invalid arguments")
            return
        self.s.sendall("exit\n".encode())

    def do_locale(self, arg):
        """Locale."""
        self.s.sendall(f"locale {arg}\n".encode())

    def do_documentation(self, arg):
        """Open documentation."""
        webbrowser.open(f"{os.path.dirname(__file__)}/../docs/_build/html/index.html")


def msg_receiver(client):
    """Receiving messages."""
    while res := client.s.recv(1024).rstrip().decode():
        print(f"\n{res}\n{client.prompt}{readline.get_line_buffer()}", end="", flush=True)


def start_client(username, host="localhost", port=1337):
    """Start client."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        client = clientCmd(s)
        handler = threading.Thread(target=msg_receiver, args=(client,))
        handler.start()
        s.sendall(f"entrance {username}\n".encode())
        client.cmdloop()
