import unittest
import socket
import multiprocessing
import asyncio
import msg.server as server
import sys
import time


def send_and_receive_command(cmd, socket):
    socket.sendall((cmd + '\n').encode())
    response = socket.recv(1024).decode().strip()
    return response


def start_server():
    sys.stdout = open('/dev/null', 'w')
    asyncio.run(server.start())


class TestClientServerCommands(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.proc = multiprocessing.Process(
                target=start_server)
        cls.proc.start()
        time.sleep(1)
        cls.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cls.s.connect(('localhost', 1337))
        cls.s.sendall(('entrance test\n').encode())
        cls.s.recv(1024)

    def test_1(self):
        response = send_and_receive_command('create_chat new', self.s)
        self.assertEqual(response, 'You successfully create new chat new')
        
    def test_2(self):
        response = send_and_receive_command('open_chat new', self.s)
        self.assertEqual(response, '_____________NEW______________')

    def test_3(self):
        response = send_and_receive_command('send msg -m cowsay sheep', self.s)
        ans = r'''<0>
(test)


 _____ 
< msg >
 ----- 
  \
   \
       __     
      UooU\.'@@@@@@`.
      \__/(@@@@@@@@@@)
           (@@@@@@@@)
           `YY~~~~YY'
            ||    ||'''
        self.assertEqual(response, ans)

    def test_4(self):
        response = send_and_receive_command('locale ru_RU.UTF-8', self.s)
        ans = 'Установлена локаль: ru_RU.UTF-8'
        self.assertEqual(response, ans)

    @classmethod
    def tearDownClass(cls):
        cls.s.close()
        cls.proc.terminate()
