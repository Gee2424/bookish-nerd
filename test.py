import requests
from tkinter import *
from tkinter import messagebox

def center_window(width=300, height=200):
    # get screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))

def validate_isbn(isbn):
    return isbn.isdigit() and len(isbn) in [10, 13]

def search_books():
    query = entry.get()
    if not validate_isbn(query):
        messagebox.showerror("Error", "Invalid ISBN. It should be either 10 or 13 digits.")
        return

    listbox.delete(0, END)  # clear the listbox
    try:
        response = requests.get(f"https://openlibrary.org/api/books?bibkeys=ISBN:{query}&format=json&jscmd=data")
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

        books = response.json()
        for book in books.values():
            listbox.insert(END, f'Title: {book["title"]}')
            listbox.insert(END, f'Author: {book["authors"][0]["name"]}')
            listbox.insert(END, f'Publish Date: {book.get("publish_date", "N/A")}')
            listbox.insert(END, f'Subjects: {", ".join([subject["name"] for subject in book.get("subjects", [])])}')
            listbox.insert(END, f'Cover Image: {book.get("cover", {}).get("medium", "N/A")}')
            listbox.insert(END, '')
    except requests.HTTPError as http_err:
        messagebox.showerror("HTTP Error", f"HTTP error occurred: {http_err}")
    except requests.RequestException as req_err:
        messagebox.showerror("Request Error", f"Other error occurred: {req_err}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def clear_results():
    listbox.delete(0, END)

root = Tk()
root.title("Book Finder App")
center_window(600, 400)  # Set window size and center on screen

Label(root, text="Enter an ISBN:").pack()

entry = Entry(root, width=50)
entry.pack()

Button(root, text="Search", command=search_books).pack()
Button(root, text="Clear", command=clear_results).pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

listbox = Listbox(root, width=75, height=20, yscrollcommand=scrollbar.set)
listbox.pack()

scrollbar.config(command=listbox.yview)

root.mainloop()
