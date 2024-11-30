import socket  # noqa: F401

def handle(client):
    try:
        data = client.recv(1024).decode("utf-8")
        print(f"Received data:\n{data}")

        # Initialize a default response for edge cases
        response = "HTTP/1.1 400 Bad Request\r\n\r\n"

        if data:
            lines = data.split("\r\n")
            request_line = lines[0] if lines else ""
            parts = request_line.split(" ")
            if len(parts) >= 3:
                method, path, _ = parts

                # Handle only GET requests
                if method == "GET":
                    if path == "/":
                        response = "HTTP/1.1 200 OK\r\n\r\n"
                    elif path.startswith("/echo/"):
                        value = path.split("/echo/")[1]
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(value)}\r\n\r\n{value}"
                    elif path.startswith("/user-agent"):
                        user_agent = "Unknown"  # Default if the header is not found
                        for header in lines[1:]:  # Start from the second line (headers begin after the request line)
                            if header.lower().startswith("user-agent:"):
                                user_agent = header.split(": ", 1)[1]
                                break
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {len(user_agent)}\r\n\r\n{user_agent}"
                    else:
                        response = "HTTP/1.1 404 Not Found\r\n\r\n"
                else:
                    response = "HTTP/1.1 405 Method Not Allowed\r\n\r\n"

        # Send the response
        client.sendall(response.encode("utf-8"))
        print(f"Sent response:\n{response}")
    except Exception as e:
        print(f"Error while handling client: {e}")
    finally:
        client.close()

def main():
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221))
    try:
        print("Server is running on localhost:4221...")
        while True:
            server_socket.listen()
            client, addr = server_socket.accept()
            print(f"Connection from {addr} has been established")
            handle(client)
    except KeyboardInterrupt:
        print("Shutting down server")
    finally:
        server_socket.close()
        print("Server socket closed. Server shutdown")

if __name__ == "__main__":
    main()
