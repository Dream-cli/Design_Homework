import re
import sys
import time
import queue
import threading
from socket import *

RSIZE = 1024
MAX_QUEUE = 64
MAX_CONNECTION = 8


def pack_encode(user_name, message, send_time=time.ctime()):
    packaging = '<user>{}</user>\n<time>{}</time>\n<msg>{}</msg>\n'.\
                format(user_name, send_time, message)
    return packaging.encode('utf-8')


def unpack_decode(data):
    packaging = data.decode('utf-8')
    send_time = re.search(r'<time>(.+)</time>', packaging).group()[6:-7]
    message = re.search(r'<msg>(.+)</msg>', packaging).group()[5:-6]
    user_name = re.search(r'<user>(.+)</user>', packaging).group()[6:-7]
    return user_name, send_time, message


def write(path, text, lock):
    lock.acquire()
    with open(path, mode='a', encoding='utf-8') as outfile:
        print(text, file=outfile)
    lock.release()


class Manager:
    def __init__(self, ip, port, log_path):
        self._ip = ip
        self._port = port
        self._log_path = log_path
        self._chatters = {}
        self._message_queue = queue.Queue()
        self._lock = threading.RLock()
        self.connect_Chatter()

    def connect_Chatter(self):
        server = socket(AF_INET, SOCK_STREAM)
        server.bind((self._ip, self._port))
        server.listen(MAX_CONNECTION)
        print('Server is start...\n{}'.format(time.ctime()))
        send_thread = threading.Thread(target=self.send_out)
        send_thread.start()
        control_thread = threading.Thread(target=self.control_Quit)
        control_thread.start()
        while True:
            conn, addr = server.accept()
            receive_thread = threading.Thread(target=self.receive_in,
                                              args=(conn, addr))
            receive_thread.start()

    def control_Quit(self):
        while True:
            command = input()
            if not command:
                continue
            elif command == 'CLOSE ALL USER':
                end_time = time.ctime()
                print('-{}-\n--Meeting is over!--'.format(end_time))
                write(self._log_path, '-{}-\n--Meeting is over!--'.format(end_time), self._lock)
                for user in self._chatters.keys():
                    self._chatters[user][0].send(pack_encode('Manager', 'Meeting is over, you are rejected!', end_time))
                    self._chatters[user][0].close()
                self._chatters.clear()
            elif re.search(r'CLOSE \S+', command):
                user = re.search(r'CLOSE \S+', command).group()[6:]
                if user in self._chatters.keys():
                    send_time = time.ctime()
                    self._chatters[user][0].send(pack_encode('Manager', 'You are rejected!', send_time))
                    str_pattern = '----\n-{}-\n{} is rejected by Manager.\n----'.format(send_time, user)
                    print(str_pattern)
                    write(self._log_path, str_pattern, self._lock)
                    for item in self._chatters.keys():
                        if item != user:
                            self._chatters[item][0].send(pack_encode('Manager',
                                                                     '{} is rejected by Manager'.format(user),
                                                                     send_time))
                    self._chatters[user][0].close()
                    del self._chatters[user]
                else:
                    print('Wrong User Name!')
            else:
                print('Wrong Input!')

    def receive_in(self, conn, addr):
        data = conn.recv(RSIZE)
        user_name, connect_time, message = unpack_decode(data)
        str_pattern = 'User-{} connected. -{}'.format(user_name, connect_time)
        print(str_pattern)
        write(self._log_path, str_pattern, self._lock)
        self._chatters[user_name] = (conn, addr)
        for user in self._chatters.keys():
            if user != user_name:
                self._chatters[user][0].send(pack_encode(user_name, 'I join the chat room!', time.ctime()))

        while True:
            try:
                data_pack = conn.recv(RSIZE)
                self._message_queue.put(data_pack)
            except:
                break

    def send_out(self):
        while True:
            data = self._message_queue.get()
            user_name, connect_time, message = unpack_decode(data)
            str_pattern = '\nTime-{}-\n[{}]:{}'.\
                format(connect_time, user_name, message)
            print(str_pattern)
            write(self._log_path, str_pattern, self._lock)

            direct_users = re.findall(r'@\S+', message)
            valid_users = []
            for item in direct_users:
                direct_user = item[1:]
                if direct_user in self._chatters.keys():
                    valid_users.append(direct_user)
            if len(valid_users):
                for valid_user in valid_users:
                    self._chatters[valid_user][0].send(data)
            else:
                for user in self._chatters.keys():
                    if user != user_name:
                        self._chatters[user][0].send(data)

            if message == 'BYEBYE':
                self._chatters[user_name][0].close()
                del self._chatters[user_name]
                str_pattern = 'User-{} departed from the chat room. -{}'.format(user_name, time.ctime())
                print(str_pattern)
                write(self._log_path, str_pattern, self._lock)
                for user in self._chatters.keys():
                    if user != user_name:
                        self._chatters[user][0].send(pack_encode(user_name,
                                                                 'I depart from the chat room!', time.ctime()))


class Chatter:
    def __init__(self, ip, port, name, log_path):
        self._ip = ip
        self._port = port
        self._name = name
        self._lock = threading.RLock()
        self._log_path = log_path + '\\{}_records.txt'.format(self._name)
        self.connect_Manager()

    def connect_Manager(self):
        client = socket(AF_INET, SOCK_STREAM)
        client.connect((self._ip, self._port))
        self._client = client
        connect_time = time.ctime()
        print('User:{} Connected. {}\n'.format(self._name, connect_time))
        sender_thread = threading.Thread(target=self.send_out)
        sender_thread.start()
        receiver_thread = threading.Thread(target=self.receive_in)
        receiver_thread.start()

    def receive_in(self):
        while True:
            try:
                data = self._client.recv(RSIZE)
                user_name, send_time, message = unpack_decode(data)
                str_pattern = '-{}-\n[{}]: {}'.format(send_time, user_name,
                                                      message)
                write(self._log_path, str_pattern, self._lock)
                print(str_pattern)
            except:
                if self._client:
                    self._client.close()
                break

    def send_out(self):
        data = pack_encode(self._name, 'CONNECT', time.ctime())
        self._client.send(data)
        while True:
            try:
                message = input()
                if not message:
                    continue
                send_time = time.ctime()
                data = pack_encode(self._name, message, send_time)
                self._client.send(data)
                str_pattern = '-{}-\n[{}]:{}'.format(send_time, self._name,
                                                     message)
                write(self._log_path, str_pattern, self._lock)
            except:
                if self._client:
                    self._client.close()
                break


if __name__ == '__main__':
    ip = '127.0.0.1'
    port = 8001
    Manager_log_path = "D:\\data\\MyChatRoom\\Manager_logs\\log.txt"
    Client_log_path = "D:\\data\\MyChatRoom\\Chatter_logs"
    mode = sys.argv[1]
    if mode == 'client':
        name = input('Enter your user name:')
        chatter_i = Chatter(ip, int(port), name, Client_log_path)
    elif mode == 'server':
        manager = Manager(ip, int(port), Manager_log_path)
