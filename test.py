import requests
from tkinter import *
from tkinter import messagebox

def search_books():
    query = entry.get()
    try:
        response = requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{query}&format=json&jscmd=data")
        books = response.json()
        for book in books.values():
            listbox.insert(END, f'Title: {book["title"]}')
            listbox.insert(END, f'Author: {book["authors"][0]["name"]}')
            listbox.insert(END, '')
    except Exception as e:
        messagebox.showerror("Error", e)

root = Tk()
root.title("Book Finder App")

Label(root, text="Enter an ISBN:").pack()

entry = Entry(root, width=50)
entry.pack()

Button(root, text="Search", command=search_books).pack()

listbox = Listbox(root, width=75, height=20)
listbox.pack()

root.mainloop()
