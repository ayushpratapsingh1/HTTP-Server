import socket
import threading
import sys
import os

def main():
    def handle_req(client, addr):
        try:
            data = client.recv(1024).decode()
            if not data:
                return
            
            req = data.split("\r\n")
            request_line = req[0].split(" ")
            method = request_line[0]
            path = request_line[1]

            if method == "GET":
                if path == "/":
                    response = "HTTP/1.1 200 OK\r\n\r\n".encode()
                elif path.startswith('/echo'):
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(path[6:])}\r\n\r\n{path[6:]}".encode()
                elif path.startswith("/user-agent"):
                    # Find User-Agent header
                    user_agent = next((header.split(": ")[1] for header in req if header.startswith("User-Agent:")), "Unknown")
                    response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}".encode()
                elif path.startswith("/files"):
                    directory = sys.argv[2] if len(sys.argv) > 2 else "."
                    filename = path[7:]
                    file_path = os.path.join(directory, filename)
                    try:
                        with open(file_path, "r") as f:
                            body = f.read()
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()
                    except FileNotFoundError:
                        response = "HTTP/1.1 404 Not Found\r\n\r\nFile not found".encode()
                    except Exception as e:
                        response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}".encode()
                else:
                    response = "HTTP/1.1 404 Not Found\r\n\r\nInvalid path".encode()
                client.send(response)

            elif method == "POST":
                if path.startswith("/files"):
                    directory = sys.argv[2] if len(sys.argv) > 2 else "."
                    filename = path[7:]
                    body = data.split("\r\n\r\n", 1)[-1]  # Extract the body after headers
                    file_path = os.path.join(directory, filename)
                    try:
                        with open(file_path, "w") as f:
                            f.write(body)
                        response = "HTTP/1.1 201 Created\r\n\r\nFile created successfully".encode()
                    except Exception as e:
                        response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}".encode()
                    client.send(response)
            else:
                response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n".encode()
                client.send(response)
        except Exception as e:
            response = f"HTTP/1.1 500 Internal Server Error\r\n\r\n{str(e)}".encode()
            client.send(response)
        finally:
            client.close()

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server started on localhost:4221")
    while True:
        try:
            client, addr = server_socket.accept()
            threading.Thread(target=handle_req, args=(client, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break
    server_socket.close()

if __name__ == "__main__":
    main()
