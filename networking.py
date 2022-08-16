'''
Client for transferring files from the security camera.
'''
import socket
import os


PORT = 4444
HOST_NAME = 'PUT HOST-NAME HERE'
ADDRESS = (HOST_NAME, PORT)
INITIAL_MSG_LEN = 64


def pad_str(s: str, padding: int) -> str:
    return (padding - len(s))*' ' + s


def send_n_bytes(sock: socket.socket, data: bytes):
    length_sent = 0
    while length_sent < len(data):
        sent = sock.send(data[length_sent:])

        if sent == 0:
            raise ConnectionAbortedError()

        length_sent = length_sent + sent


def get_path_base_name(filepath: str) -> str:
    return os.path.basename(os.path.normpath(filepath))


def send_file(sock: socket.socket, filepath: str):
    filename = get_path_base_name(filepath)
    if len(filename) > 64:
        raise RuntimeError('Name of file too long!')

    with open(filepath, 'rb') as f:
        content = f.read()

    message_len_bytes = pad_str(str(len(content)), INITIAL_MSG_LEN).encode()
    filename_bytes = pad_str(filename, INITIAL_MSG_LEN).encode()

    send_n_bytes(sock, message_len_bytes + filename_bytes)
    send_n_bytes(sock, content)
