'''
Server for transferring files from the security camera.
'''
import socket
import threading
import os

PORT = 4444
HOST_NAME = socket.gethostname()
ADDRESS = (HOST_NAME, PORT)
MAX_UNACCEPTED_SOCKET_CONNECTIONS = 5
INITIAL_MSG_LEN = 64

def recv_n_bytes(sock: socket.socket, length: int) -> bytes:
    length_received = 0

    result = b''

    while length_received < length:
        chunk = sock.recv(min(length - length_received, 2048))

        if len(chunk) == 0:
            raise ConnectionAbortedError()

        result += chunk
        length_received += len(chunk)

    return result


def extract_metadata(s: str) -> tuple[int, str]:
    msg_content_length = int(s[:INITIAL_MSG_LEN])
    filename = s[INITIAL_MSG_LEN:].strip()

    return msg_content_length, filename

file_lock = threading.Lock()

def handle_client(sock: socket.socket, address: str):
    print(f'[NEW CONNECTION] {address[0]}')

    while True:
        try:
            metadata_msg = recv_n_bytes(sock, INITIAL_MSG_LEN*2).decode('utf-8')
            msg_content_len, filename = extract_metadata(metadata_msg)
        except UnicodeDecodeError:
            print(f'[ERROR] Initial message of {address[0]} could not be converted to utf-8')
            continue
        except ValueError:
            print(f'[ERROR] Initial message of {address[0]} could not be converted to integer')
            continue
        except ConnectionAbortedError:
            print(f'[{address[0]}] Connection aborted. Cleaning up...')

            sock.shutdown(socket.SHUT_RDWR)
            sock.close()

            print(f'[{address[0]}] Done!')

            return

        data = recv_n_bytes(sock, msg_content_len)

        with file_lock, open(os.path.join('server-files/' + filename), 'wb') as f:
            f.write(data)

def main():
    '''
    main is the main function of the program.
    '''
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(ADDRESS)
    serversocket.listen(MAX_UNACCEPTED_SOCKET_CONNECTIONS)
    print('[SERVER STARTING] Server is now listening...')

    while True:
        clientsocket, address = serversocket.accept() 

        thread = threading.Thread(target=handle_client, args=(clientsocket, address,))
        thread.start()

        print(f'[ACTIVE CONNECTIONS] {threading.active_count() - 1}')

if __name__ == '__main__':
    main()
