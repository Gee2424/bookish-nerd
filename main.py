import os
import requests
import tkinter as tk
from tkinter import messagebox, ttk
from threading import Thread


class BookFinderAPI:
    def __init__(self):
        self.base_url = "https://www.googleapis.com/books/v1/volumes"
        self.api_key = os.getenv('GOOGLE_BOOK_API_KEY')  # Assuming you have set this environment variable.

    def search_books(self, query):
        response = requests.get(f"{self.base_url}?q={query}&key={self.api_key}")
        return response.json()


class BookFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Finder App")
        self.api = BookFinderAPI()
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.validate_input)
        self.create_widgets()

    def create_widgets(self):
        label = ttk.Label(self.root, text="Enter a title, author, or genre:")
        label.pack(pady=10)

        self.entry = ttk.Entry(self.root, textvariable=self.search_var, width=50)
        self.entry.pack()

        self.search_button = ttk.Button(self.root, text="Search", command=self.search_books, state='disabled')
        self.search_button.pack(pady=10)

        self.result_listbox = tk.Listbox(self.root, width=60, height=20)
        self.result_listbox.pack(pady=10)

    def validate_input(self, *args):
        query = self.search_var.get()
        if query:
            self.search_button['state'] = 'normal'
        else:
            self.search_button['state'] = 'disabled'

    def search_books(self):
        self.result_listbox.delete(0, 'end')

        query = self.search_var.get()

        try:
            self.root.config(cursor="wait")  # Set wait cursor while fetching data.
            Thread(target=self.fetch_and_display_books, args=(query,)).start()
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Error occurred during the search: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def fetch_and_display_books(self, query):
        books = self.api.search_books(query)
        self.root.after(0, self.root.config, {"cursor": ""})  # Reset the cursor.
        if "items" in books:
            for book in books["items"]:
                title = book["volumeInfo"].get("title", "N/A")
                authors = ", ".join(book["volumeInfo"].get("authors", ["N/A"]))
                self.result_listbox.insert('end', f"Title: {title}\nAuthor(s): {authors}\n")
        else:
            messagebox.showinfo("No Results", "No books found for the given query.")

if __name__ == "__main__":
    root = tk.Tk()
    app = BookFinderApp(root)
    root.mainloop()
