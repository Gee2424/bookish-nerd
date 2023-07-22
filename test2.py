import requests
import sqlite3
from tkinter import *
from tkinter import messagebox

def center_window(width=300, height=200):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def validate_isbn(isbn):
    return isbn.isdigit() and len(isbn) in [10, 13]

def search_books():
    query = entry.get()
    listbox.delete(0, END)
    try:
        response = requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{query}&format=json&jscmd=data")
        response.raise_for_status()

        books = response.json()
        for book in books.values():
            listbox.insert(END, f'Title: {book["title"]}')
            listbox.insert(END, f'Author: {book["authors"][0]["name"]}')
            listbox.insert(END, '')
    except requests.HTTPError as http_err:
        messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
    except requests.RequestException as req_err:
        messagebox.showerror("Request Error", f"Other error occurred: {req_err}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def add_to_favorites():
    selected = listbox.curselection()
    if not selected:
        return
    title = listbox.get(selected[0])
    author = listbox.get(selected[0]+1)
    conn = sqlite3.connect('favorites.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS favorites (title TEXT, author TEXT)")
    c.execute("INSERT INTO favorites VALUES (?,?)", (title[7:], author[8:]))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", "Book added to favorites")

def show_favorites():
    listbox.delete(0, END)
    conn = sqlite3.connect('favorites.db')
    c = conn.cursor()
    c.execute("SELECT * FROM favorites")
    rows = c.fetchall()
    conn.close()
    for row in rows:
        listbox.insert(END, f'Title: {row[0]}')
        listbox.insert(END, f'Author: {row[1]}')
        listbox.insert(END, '')

root = Tk()
root.title("Book Finder App")
center_window(600, 400)

Label(root, text="Enter an ISBN:").pack()

entry = Entry(root, width=50)
entry.pack()

Button(root, text="Search", command=search_books).pack()
Button(root, text="Add to Favorites", command=add_to_favorites).pack()
Button(root, text="Show Favorites", command=show_favorites).pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

listbox = Listbox(root, width=75, height=20, yscrollcommand=scrollbar.set)
listbox.pack()

scrollbar.config(command=listbox.yview)

root.mainloop()
