from fastapi import FastAPI, Depends, HTTPException, Form, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from typing import List
from sqlalchemy import Column, Integer, String, create_engine, or_
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os


# FastAPI instance 
app = FastAPI()


# Database URL (SQLite file database) 
DATABASE_URL = "sqlite:///./books.db"


# Secret Key for JWT
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Function to create JWT Token
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Function to decode and verify JWT toke 
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# SQLAlchemy Engine and Session 
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model for database
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


# Password hashing
pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# SQLAlchemy Book Model 
class BookDB(Base):
    __tablename__="books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)

# Create Tables
Base.metadata.create_all(bind=engine)

# Pydantic schema for validation
class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    author: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., gt=1900, lt=2026)
    category: str = Field(..., min_length=3, max_length=50)

# Dependency to get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get a user (GET)
def get_current_user(token: str = Security(oauth2_scheme)):
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["sub"]


# CRUD Operations 

# Create a Book (POST)
@app.post("/books/", response_model=Book)
def create_book(book: Book, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_book = BookDB(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


# Read Books (GET)

# Get all books
@app.get("/books/", response_model=list[Book])
def get_books(
    category: str = None,
    search: str = None, 
    limit: int = 10,
    offset: int = 0,
    sort_by: str = "title",
    order: str = "asc",
    db: Session=Depends(get_db)
):
    query = db.query(BookDB)
    if category:
        query = query.filter(BookDB.category == category)
    
    if search:
        query = query.filter(
            or_(
                BookDB.title.ilike(f"%{search}%"),
                BookDB.author.ilike(f"%{search}%")
            )
        )
    
    if sort_by in ["title", "author", "year"]:
        column = getattr(BookDB, sort_by)
        if order == "desc":
            column = column.desc()
        query = query.order_by(column)
    
    books = query.offset(offset).limit(limit).all()
    return books

# Get a specific book by ID
@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session=Depends(get_db)):
    book = db.query(BookDB).filter(BookDB.id==book_id).first()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


# Update a Book (PUT)
@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book: Book, db: Session=Depends(get_db)):
    db_book = db.query(BookDB).filter(BookDB.id==book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for key, value in book.dict().items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book


# Delete a Book (DELETE)
@app.delete("/books/{book_id}", response_model=Book)
def delete_book(book_id: int, db: Session=Depends(get_db)):
    db_book = db.query(BookDB).filter(BookDB.id==book_id).first()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    db.delete(db_book)
    db.commit()
    return db_book


# Create a user (POST)
@app.post("/signup/")
def signup(username: str = Form(...), password: str = Form(...), db: Session=Depends(get_db)):
    existing_user = db.query(User).filter(User.username==username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    hashed_password = hash_password(password)
    new_user = User(username=username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


# Login as user (POST)
@app.post("/token/")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username==username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid Credentials")
    
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
    

@app.get("/")
def home():
    return {"message": "Welcome to the BookStore API!"}