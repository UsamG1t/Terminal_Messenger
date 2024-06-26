import unittest
import unittest.mock as mock
import msg.client as client
from io import StringIO


class TestClient(unittest.TestCase):
    def test_0(self):
        with (
                mock.patch('sys.stdin', StringIO("create_chat new_chat")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('msg.client.msg_receiver', return_value=True)
             ):
            client.start_client("test", False)
            sendall_call = socket_mock.mock_calls[3].args[0]
            self.assertEqual(sendall_call, b'create_chat new_chat\n')

    def test_1(self):
        with (
                mock.patch('sys.stdin', StringIO("open_chat new_chat")),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('msg.client.msg_receiver', return_value=True)
             ):
            client.start_client("test", False)
            sendall_call = socket_mock.mock_calls[3].args[0]
            self.assertEqual(sendall_call, b'open_chat new_chat\n')

    def test_2(self):
        command = "create_chat new_chat\nshow_chatlist"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('socket.socket', autospec=True) as socket_mock,
                mock.patch('msg.client.msg_receiver', return_value=True)
             ):
            client.start_client("test", False)
            sendall_call = socket_mock.mock_calls[4].args[0]
            self.assertEqual(sendall_call, b'show_chatlist\n')

    def test_3(self):
        command = "add_to_chat masha"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('builtins.print', autospec=True) as output_mock,
                mock.patch('socket.socket', autospec=True),
                mock.patch('msg.client.msg_receiver', return_value=True)
             ):
            client.start_client("test", False)
            output_call = output_mock.mock_calls[0].args[0]
            self.assertEqual(output_call, 'you need to write username and chat name')

    def test_4(self):
        command = "add_to_favourites"
        with (
                mock.patch('sys.stdin', StringIO(command)),
                mock.patch('builtins.print', autospec=True) as output_mock,
                mock.patch('socket.socket', autospec=True),
                mock.patch('msg.client.msg_receiver', return_value=True)
             ):
            client.start_client("test", False)
            output_call = output_mock.mock_calls[0].args[0]
            self.assertEqual(output_call, 'you need to write message id')
