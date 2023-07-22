import requests
import sqlite3
from tkinter import *
from tkinter import messagebox
import json

class BookFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Finder App")
        self.center_window(600, 400)
        self.favorites_db = "favorites.db"
        self.cache = {}

        Label(self.root, text="Enter an ISBN:").pack()

        self.isbn_var = StringVar()
        self.entry = Entry(self.root, width=50, textvariable=self.isbn_var)
        self.entry.pack()

        self.isbn_length_var = StringVar(value="10")
        Spinbox(self.root, from_=10, to=13, textvariable=self.isbn_length_var).pack()

        Label(self.root, text="Select a subject for book suggestions:").pack()
        self.subjects_var = StringVar(value=["Science", "Fiction", "History"])
        self.subjects_listbox = Listbox(self.root, listvariable=self.subjects_var, selectmode=MULTIPLE)
        self.subjects_listbox.pack()

        Button(self.root, text="Search", command=self.search_books).pack()
        Button(self.root, text="Add to Favorites", command=self.add_to_favorites).pack()
        Button(self.root, text="Show Favorites", command=self.show_favorites).pack()
        Button(self.root, text="Suggest Books", command=self.suggest_books).pack()

        self.scrollbar = Scrollbar(self.root)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.listbox = Listbox(self.root, width=75, height=20, yscrollcommand=self.scrollbar.set)
        self.listbox.pack()

        self.scrollbar.config(command=self.listbox.yview)

    def center_window(self, width=300, height=200):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def validate_isbn(self, isbn):
        return isbn.isdigit() and len(isbn) == int(self.isbn_length_var.get())

    def search_books(self):
        query = self.isbn_var.get()
        if not self.validate_isbn(query):
            messagebox.showerror("Invalid ISBN", "Please enter a valid ISBN.")
            return
        self.listbox.delete(0, END)
        if query in self.cache:
            self.display_books(self.cache[query])
        else:
            try:
                response = requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{query}&format=json&jscmd=data")
                response.raise_for_status()

                books = response.json()
                self.cache[query] = books
                self.display_books(books)
            except requests.HTTPError as http_err:
                messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
            except requests.RequestException as req_err:
                messagebox.showerror("Request Error", f"Other error occurred: {req_err}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def display_books(self, books):
        for book in books.values():
            self.listbox.insert(END, f'Title: {book["title"]}')
            self.listbox.insert(END, f'Author: {book["authors"][0]["name"]}')
            self.listbox.insert(END, '')

    def add_to_favorites(self):
        selected = self.listbox.curselection()
        if not selected:
            return
        title = self.listbox.get(selected[0])
        author = self.listbox.get(selected[0]+1)
        try:
            with sqlite3.connect(self.favorites_db) as conn:
                c = conn.cursor()
                c.execute("CREATE TABLE IF NOT EXISTS favorites (title TEXT, author TEXT)")
                c.execute("INSERT INTO favorites VALUES (?,?)", (title[7:], author[8:]))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred with the database: {e}")
        else:
            messagebox.showinfo("Success", "Book added to favorites")

    def show_favorites(self):
        self.listbox.delete(0, END)
        try:
            with sqlite3.connect(self.favorites_db) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM favorites")
                rows = c.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred with the database: {e}")
        else:
            for row in rows:
                self.listbox.insert(END, f'Title: {row[0]}')
                self.listbox.insert(END, f'Author: {row[1]}')
                self.listbox.insert(END, '')

    def suggest_books(self):
        self.listbox.delete(0, END)
        subjects = [self.subjects_listbox.get(i) for i in self.subjects_listbox.curselection()]
        if not subjects:
            messagebox.showinfo("No Subjects Selected", "Please select one or more subjects for book suggestions.")
            return
        for subject in subjects:
            try:
                response = requests.get(f"https://openlibrary.org/subjects/{subject.lower()}.json")
                response.raise_for_status()
                data = response.json()
                books = data["works"][:5]  # Get top 5 books
                for book in books:
                    self.listbox.insert(END, f'Title: {book["title"]}')
                    self.listbox.insert(END, f'Author: {", ".join(author["name"] for author in book["authors"])}')
                    self.listbox.insert(END, '')
            except requests.HTTPError as http_err:
                messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
            except requests.RequestException as req_err:
                messagebox.showerror("Request Error", f"Other error occurred: {req_err}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    root = Tk()
    app = BookFinder(root)
    root.mainloop()
