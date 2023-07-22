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

def search_books():
    query = characteristics_var.get()
    listbox.delete(0, END)  # clear the listbox
    try:
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}")
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx

        books = response.json()
        for book in books["items"]:
            volume_info = book["volumeInfo"]
            listbox.insert(END, f'Title: {volume_info["title"]}')
            listbox.insert(END, f'Author: {", ".join(volume_info.get("authors", ["N/A"]))}')
            listbox.insert(END, f'Published Date: {volume_info.get("publishedDate", "N/A")}')
            listbox.insert(END, f'Categories: {", ".join(volume_info.get("categories", ["N/A"]))}')
            listbox.insert(END, f'Description: {volume_info.get("description", "N/A")}')
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

characteristics = ["Fiction", "Non-fiction", "Romance", "Sci-Fi", "Mystery", "Biography", "Comedy"]
characteristics_var = StringVar()
characteristics_var.set(characteristics[0])  # default value

Label(root, text="Select a genre:").pack()

OptionMenu(root, characteristics_var, *characteristics).pack()

Button(root, text="Suggest Books", command=search_books).pack()
Button(root, text="Clear", command=clear_results).pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

listbox = Listbox(root, width=75, height=20, yscrollcommand=scrollbar.set)
listbox.pack()

scrollbar.config(command=listbox.yview)

root.mainloop()
