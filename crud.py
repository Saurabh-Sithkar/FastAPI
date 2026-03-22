from fastapi import FastAPI,status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

app= FastAPI()
books= [
    {"id": 1, "title": "Book One", "author": "Author One"},
    {"id": 2, "title": "Book Two", "author": "Author Two"},
    {"id": 3, "title": "Book Three", "author": "Author  Three"},
    {"id": 4, "title": "Book Four", "author": "Author Four"}
]

@app.get("/books")
def get_books():
    return books

@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found") 


class Book(BaseModel):
    id: int
    title: str
    author: str

@app.post("/books")
def create_book(book: Book):
    new_book = book.model_dump()
    books.append(new_book)  
   
class BookUpdate(BaseModel):
    title: str
    author: str

@app.put("/books/{book_id}")
def update_book(book_id: int, book_update: BookUpdate):
    for book in books:
        if book["id"] == book_id:
            book["title"] = book_update.title
            book["author"] = book_update.author
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

