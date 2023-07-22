import requests
import sqlite3
from tkinter import *
from tkinter import messagebox
import urllib.parse

class BookFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Finder App")
        self.center_window(800, 600)
        self.favorites_db = "favorites.db"
        self.cache = {}

        self.input_frame = Frame(self.root)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        Label(self.input_frame, text="Enter a book title:").grid(row=0, column=0, sticky='w')
        self.title_var = StringVar()
        self.entry = Entry(self.input_frame, width=50, textvariable=self.title_var)
        self.entry.grid(row=0, column=1, sticky='w')

        Label(self.input_frame, text="Select a subject for book suggestions:").grid(row=1, column=0, sticky='w')
        self.subjects_var = StringVar(value=["Science", "Fiction", "History"])
        self.subjects_listbox = Listbox(self.input_frame, listvariable=self.subjects_var, selectmode=MULTIPLE, height=3)
        self.subjects_listbox.grid(row=1, column=1, sticky='w')

        self.button_frame = Frame(self.root)
        self.button_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        Button(self.button_frame, text="Search", command=self.search_books).grid(row=0, column=0, padx=5)
        Button(self.button_frame, text="Add to Favorites", command=self.add_to_favorites).grid(row=0, column=1, padx=5)
        Button(self.button_frame, text="Show Favorites", command=self.show_favorites).grid(row=0, column=2, padx=5)
        Button(self.button_frame, text="Suggest Books", command=self.suggest_books).grid(row=0, column=3, padx=5)

        self.results_frame = Frame(self.root)
        self.results_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        Label(self.results_frame, text="Search Results").grid(row=0, column=0, sticky='w')
        self.search_scrollbar = Scrollbar(self.results_frame)
        self.search_scrollbar.grid(row=1, column=1, sticky='ns')

        self.search_listbox = Listbox(self.results_frame, width=75, height=10, yscrollcommand=self.search_scrollbar.set)
        self.search_listbox.grid(row=1, column=0, sticky='nsew')

        self.search_scrollbar.config(command=self.search_listbox.yview)

        Label(self.results_frame, text="Favorites").grid(row=2, column=0, sticky='w')
        self.favorites_scrollbar = Scrollbar(self.results_frame)
        self.favorites_scrollbar.grid(row=3, column=1, sticky='ns')

        self.favorites_listbox = Listbox(self.results_frame, width=75, height=10, yscrollcommand=self.favorites_scrollbar.set)
        self.favorites_listbox.grid(row=3, column=0, sticky='nsew')

        self.favorites_scrollbar.config(command=self.favorites_listbox.yview)

    def center_window(self, width=300, height=200):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def search_books(self):
        query = self.title_var.get().strip()
        if not query:
            messagebox.showerror("Invalid input", "Please enter a valid book title.")
            return
        self.search_listbox.delete(0, END)
        self.search_listbox.insert(END, "Loading...")
        self.root.after(1, self.get_books, query)

    def get_books(self, query):
        self.search_listbox.delete(0, END)
        if query in self.cache:
            self.display_books(self.search_listbox, self.cache[query])
        else:
            try:
                response = requests.get(f"https://openlibrary.org/search.json?title={urllib.parse.quote(query)}")
                response.raise_for_status()

                books = response.json()['docs'][:5]  # Limit to top 5 results
                self.cache[query] = books
                self.display_books(self.search_listbox, books)
            except requests.HTTPError as http_err:
                messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
            except requests.RequestException as req_err:
                messagebox.showerror("Request Error", f"Other error occurred: {req_err}")
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def display_books(self, listbox, books):
        for book in books:
            listbox.insert(END, f'Title: {book.get("title", "N/A")}')
            listbox.insert(END, f'Author: {", ".join(book.get("author_name", ["N/A"]))}')
            listbox.insert(END, '')

    def add_to_favorites(self):
        selected = self.search_listbox.curselection()
        if not selected:
            return
        title = self.search_listbox.get(selected[0])
        author = self.search_listbox.get(selected[0]+1)
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
        self.favorites_listbox.delete(0, END)
        try:
            with sqlite3.connect(self.favorites_db) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM favorites")
                rows = c.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred with the database: {e}")
        else:
            for row in rows:
                self.favorites_listbox.insert(END, f'Title: {row[0]}')
                self.favorites_listbox.insert(END, f'Author: {row[1]}')
                self.favorites_listbox.insert(END, '')

    def suggest_books(self):
        self.search_listbox.delete(0, END)
        subjects = [self.subjects_listbox.get(i) for i in self.subjects_listbox.curselection()]
        if not subjects:
            messagebox.showinfo("No Subjects Selected", "Please select one or more subjects for book suggestions.")
            return
        self.search_listbox.insert(END, "Loading...")
        self.root.after(1, self.get_suggested_books, subjects)

    def get_suggested_books(self, subjects):
        self.search_listbox.delete(0, END)
        for subject in subjects:
            if subject in self.cache:
                self.display_books(self.search_listbox, self.cache[subject])
            else:
                try:
                    response = requests.get(f"https://openlibrary.org/subjects/{subject.lower()}.json")
                    response.raise_for_status()
                    data = response.json()
                    books = data["works"][:5]  # Get top 5 books
                    self.cache[subject] = books
                    self.display_books(self.search_listbox, books)
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
