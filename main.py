from fastapi import FastAPI, Request, Response
import uvicorn
import pymongo
import urllib.parse
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorClient
from models import Book, Author
from typing import List
from bson.objectid import ObjectId


app = FastAPI()

MY_PASSWORD = ''
DB_NAME = 'booksdb'
COLLECTION_NAME = "books"

DB_URL = 'mongodb+srv://mjtoolbox:' + urllib.parse.quote_plus(MY_PASSWORD) + '@cluster0.za47k.mongodb.net/?retryWrites=true&w=majority'


@app.on_event("startup")
async def startup_event():
    # Sync
    # app.mongodb_client = pymongo.MongoClient(DB_URL)
    # Async
    app.mongodb_client = AsyncIOMotorClient(DB_URL)
    app.mongodb = app.mongodb_client[DB_NAME]


@app.on_event("shutdown")
async def shutdown_event():
    app.mongodb.close()


@app.get("/")
async def root():
    return {"message": "Hello from Fast API"}


@app.post("/test", response_model=Book)
async def test():
    book = {
        "title": "Testing",
        "authors": [
            {"name": "John Smith"},
            {"name": "Jane Tompson"}
        ]
    }
    # bookjson = jsonable_encoder(book)

    inserted_book = await app.mongodb[COLLECTION_NAME].insert_one(book)
    print(inserted_book.inserted_id)
    new_book = await app.mongodb[COLLECTION_NAME].find_one({"_id": inserted_book.inserted_id})
    # return display_helper(new_book)
    return new_book


@app.post("/book")
async def add_book(book: Book):
    bookjson = jsonable_encoder(book)
    insertedBook = await app.mongodb[COLLECTION_NAME].insert_one(bookjson)
    print(insertedBook.inserted_id)
    new_book = await app.mongodb[COLLECTION_NAME].find_one({"_id": insertedBook.inserted_id})
    return new_book


@app.get("/books", response_model=List[Book])
async def retrieve_books():
    books = []
    async for book in app.mongodb[COLLECTION_NAME].find():
        books.append(book)
    return books


@app.get("/book/{id}", response_model=Book)
async def find_book(id: str):
    book = await app.mongodb[COLLECTION_NAME].find_one({"_id": ObjectId(id)})
    return book


@app.put("/book/{id}")
async def update_book(id: str, book: Book):
    bookjson = jsonable_encoder(book)

    book = await app.mongodb[COLLECTION_NAME].find_one({"_id": ObjectId(id)})
    if book:
        updated_book = await app.mongodb[COLLECTION_NAME].update_one({"_id": ObjectId(id)}, {"$set": bookjson})
        if updated_book:
            return True
        return False


@app.delete("/book/{id}")
async def delete_book(id: str):
    book = await app.mongodb[COLLECTION_NAME].find_one({"_id": ObjectId(id)})
    if book:
        await app.mongodb[COLLECTION_NAME].delete_one({"_id": ObjectId(id)})
        return True

if __name__ == "__main__":
    # Use this for debugging purposes only
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="debug")
