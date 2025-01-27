# Bookstore API

## Overview
The **Bookstore API** is a RESTful API built using **FastAPI** that allows users to manage books, including features like searching, pagination, and sorting. The API is containerized using **Docker** to ensure smooth deployment and scalability.

## Features
- CRUD operations for books
- Search functionality
- Pagination and sorting
- JWT-based authentication
- Containerized using Docker

## Tech Stack
- **FastAPI** (Backend Framework)
- **SQLite** (Database)
- **JWT** (Authentication)
- **Docker** (Containerization)
- **Uvicorn** (ASGI Server)

## Installation
### Prerequisites
- Python 3.11+
- Docker installed
- Git installed

### Steps to Run Locally
1. Clone the repository:
   ```sh
   git clone https://github.com/Mehtab-Sidhu/bookstore.git
   cd bookstore
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Run the application:
   ```sh
   uvicorn main:app --reload
   ```

4. Access the API:
   - Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

## Running with Docker
1. Build the Docker image:
   ```sh
   docker build -t bookstore-api .
   ```

2. Run the container:
   ```sh
   docker run -p 8000:8000 bookstore-api
   ```

## API Endpoints
| Method | Endpoint       | Description         |
|--------|---------------|---------------------|
| GET    | `/books`      | Get all books      |
| GET    | `/books/{id}` | Get a book by ID   |
| POST   | `/books`      | Add a new book     |
| PUT    | `/books/{id}` | Update a book      |
| DELETE | `/books/{id}` | Delete a book      |
| POST   | `/signup/`    | Create a user      |
| POST   | `/token/`     | Login as user      |

## Contributing
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

---
Feel free to contribute and improve the project!✨
