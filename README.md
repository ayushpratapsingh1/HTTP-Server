# HTTP Server in Python

## Overview  
This project is a **lightweight HTTP server** implemented in **Python**, designed to handle **basic HTTP requests** with efficient request parsing, routing, and response generation. The server provides a foundation for hosting static content and managing simple RESTful APIs.

## Features  
- **Request Handling**  
  - Parses incoming HTTP requests (GET, POST, etc.) and generates appropriate responses.  
  - Handles query parameters, headers, and body content.  

- **Routing**  
  - Supports dynamic and static routes for flexible endpoint management.  
  - Serves static files such as HTML, CSS, and JavaScript.  

- **Error Handling**  
  - Returns appropriate HTTP status codes (e.g., 404 for Not Found, 500 for Server Errors).  
  - Provides customizable error pages for user-friendly debugging.  

- **Static File Hosting**  
  - Serves static assets from a configurable directory.  
  - MIME type handling for common file types (HTML, CSS, JS, images, etc.).  

## How It Works  
1. **Request Parsing**  
   - The server parses the HTTP request to extract the method, headers, and body.  
   - Supports URL decoding for query parameters.  

2. **Routing and Responses**  
   - Maps requested URLs to specific handler functions or static files.  
   - Dynamically generates HTTP responses based on request data.  

3. **Static Content Delivery**  
   - Reads and serves static files from a specified directory, ensuring MIME types are correctly set.  

## Example Usage  
1. Start the server:  

   ```bash
   python http_server.py
   
3. Make a GET request to fetch a static file:

   ```bash
   curl http://localhost:8080/index.html
4. Access dynamic routes:

   ```bash
   curl http://localhost:8080/hello?name=User

## Requirements
- Python 3.7 or later

## Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/http-server.git
   cd http-server

3. Install dependencies (if any):

   ```bash
   pip install -r requirements.txt

## Configuration
- Modify the server's listening port and static file directory in the http_server.py file:

   ```
   PORT = 8080
   STATIC_DIR = "./static"

## Future Enhancements
- Add HTTPS support with SSL certificates.
- Implement support for additional HTTP methods (PUT, DELETE, etc.).
- Include session and cookie management for stateful interactions.
- Provide a logging system for server activities.
