import socket
from threading import Thread
import argparse
from pathlib import Path
import gzip

RN = b'\r\n'


def parse_request(conn):
    d = {}
    headers = {}
    body = []

    target = 0  # request
    rest = b''
    ind = 0
    body_len = 0
    body_count = 0
    while data := conn.recv(1024):
        if rest:
            data = rest + data
            rest = b''

        if target == 0:
            ind = data.find(RN)
            if ind == -1:
                rest = data
                continue
            line = data[:ind].decode()
            data = data[ind + 2:]
            d['request'] = line
            l = line.split()
            d['method'] = l[0]
            d['url'] = l[1]
            target = 1

        if target == 1:
            if not data:
                continue
            while True:
                ind = data.find(RN)
                if ind == -1:
                    rest = data
                    break
                if ind == 0:
                    data = data[ind + 2:]
                    target = 2
                    break
                line = data[:ind].decode()
                data = data[ind + 2:]
                l = line.split(':', maxsplit=1)
                field = l[0]
                value = l[1].strip()
                headers[field.lower()] = value
            if target == 1:
                continue

        if target == 2:
            if 'content-length' not in headers:
                break
            body_len = int(headers['content-length'])
            if not body_len:
                break
            target = 3

        if target == 3:
            body.append(data)
            body_count += len(data)
            if body_count >= body_len:
                break

    d['headers'] = headers
    d['body'] = b''.join(body)
    return d


def req_handler(conn, dir_):
    with conn:
        d = parse_request(conn)
        url = d['url']
        method = d['method']
        headers = d['headers']

        if url.startswith('/echo/'):
            body = url[6:].encode()
            conn.send(b'HTTP/1.1 200 OK\r\n')
            conn.send(b'Content-Type: text/plain\r\n')
            if encoding := headers.get('accept-encoding', None):
                encodings = [e.strip() for e in encoding.split(',')]
                if 'gzip' in encodings:
                    compressed_body = gzip.compress(body)
                    conn.send(b'Content-Encoding: gzip\r\n')
                    conn.send(f'Content-Length: {len(compressed_body)}\r\n'.encode())
                    conn.send(RN)
                    conn.send(compressed_body)
                    return
            conn.send(f'Content-Length: {len(body)}\r\n'.encode())
            conn.send(RN)
            conn.send(body)
        else:
            conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")


def main():
    parser = argparse.ArgumentParser(description='socket server')
    parser.add_argument('--directory', default='.', help='directory from which to get files')
    args = parser.parse_args()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server started on localhost:4221")
    while True:
        try:
            conn, _ = server_socket.accept()
            Thread(target=req_handler, args=(conn, args.directory)).start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break
    server_socket.close()


if __name__ == "__main__":
    main()
