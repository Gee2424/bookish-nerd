import requests
from tkinter import *
from tkinter import messagebox

def search_books():
    query = entry.get()
    try:
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}&key={your_api_key}")
        books = response.json()
        for book in books["items"]:
            listbox.insert(END, f'Title: {book["volumeInfo"]["title"]}')
            listbox.insert(END, f'Author: {book["volumeInfo"]["authors"]}')
            listbox.insert(END, '')
    except Exception as e:
        messagebox.showerror("Error", e)

root = Tk()
root.title("Book Finder App")

Label(root, text="Enter a title, author, or genre:").pack()

entry = Entry(root, width=50)
entry.pack()

Button(root, text="Search", command=search_books).pack()

listbox = Listbox(root, width=75, height=20)
listbox.pack()

root.mainloop()