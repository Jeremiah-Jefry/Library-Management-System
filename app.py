#Library imports
import tkinter as tk
from tkinter import messagebox, simpledialog
import mysql.connector
from datetime import date

# Python MySql Connectivity
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Password123",
    database="library_db"
)
cursor = db.cursor()
cursor.execute("USE library_db")

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    author VARCHAR(255) NOT NULL,
    available BOOLEAN DEFAULT TRUE
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS borrow (
    borrow_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    borrow_date DATE,
    return_date DATE,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
)
""")
db.commit()

# Functions
def add_book():
    title = simpledialog.askstring("Add Book", "Enter book title:")
    author = simpledialog.askstring("Add Book", "Enter book author:")
    if title and author:
        cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
        db.commit()
        messagebox.showinfo("Success", "Book added successfully!")
    else:
        messagebox.showwarning("Input Error", "Title and Author cannot be empty.")

def display_books():
    listbox.delete(0, tk.END)
    cursor.execute("SELECT book_id, title, author, available FROM books")  
    for book in cursor.fetchall():
        status = "Available" if book[3] else "Borrowed"
        listbox.insert(tk.END, f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Status: {status}")

def borrow_book():
    book_id = simpledialog.askinteger("Borrow Book", "Enter book ID to borrow:")
    if book_id:
        cursor.execute("SELECT available FROM books WHERE book_id = %s", (book_id,))
        result = cursor.fetchone()
        if result and result[0]:
            cursor.execute("UPDATE books SET available = FALSE WHERE book_id = %s", (book_id,))
            cursor.execute("INSERT INTO borrow (book_id, borrow_date) VALUES (%s, %s)", (book_id, date.today()))
            db.commit()
            messagebox.showinfo("Success", "Book borrowed successfully!")
        else:
            messagebox.showwarning("Unavailable", "Book is not available for borrowing.")
    else:
        messagebox.showwarning("Input Error", "Book ID cannot be empty.")

def return_book():
    book_id = simpledialog.askinteger("Return Book", "Enter book ID to return:")
    if book_id:
        cursor.execute("SELECT available FROM books WHERE book_id = %s", (book_id,))
        result = cursor.fetchone()
        if result and not result[0]:
            cursor.execute("UPDATE books SET available = TRUE WHERE book_id = %s", (book_id,))
            cursor.execute("UPDATE borrow SET return_date = %s WHERE book_id = %s AND return_date IS NULL", (date.today(), book_id))
            db.commit()
            messagebox.showinfo("Success", "Book returned successfully!")
        else:
            messagebox.showwarning("Error", "Book is not currently borrowed.")
    else:
        messagebox.showwarning("Input Error", "Book ID cannot be empty.")

def search_book():
    search_term = simpledialog.askstring("Search Book", "Enter book title or author:")
    if search_term:
        listbox.delete(0, tk.END)
        cursor.execute("SELECT book_id, title, author, available FROM books WHERE title LIKE %s OR author LIKE %s", (f"%{search_term}%", f"%{search_term}%"))
        results = cursor.fetchall()
        if results:
            for book in results:
                status = "Available" if book[3] else "Borrowed"
                listbox.insert(tk.END, f"ID: {book[0]}, Title: {book[1]}, Author: {book[2]}, Status: {status}")
        else:
            messagebox.showinfo("No Results", "No books found matching the search criteria.")
    else:
        messagebox.showwarning("Input Error", "Search term cannot be empty.")

# GUI Setup
root = tk.Tk()
root.title("Library Management System")
root.geometry("800x450")

heading = tk.Label(root, text="Library Management System", font=("Arial", 25, "bold"))
heading.pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=20)

btn_add = tk.Button(frame, text="Add Book", width=15, command=add_book, bg="#4CAF50", fg="white")
btn_add.grid(row=0, column=0, padx=10, pady=10)

btn_display = tk.Button(frame, text="Display Books", width=15, command=display_books, bg="#2196F3", fg="white")
btn_display.grid(row=0, column=1, padx=10, pady=10)

btn_borrow = tk.Button(frame, text="Borrow Book", width=15, command=borrow_book, bg="#9C27B0", fg="white")
btn_borrow.grid(row=1, column=0, padx=10, pady=10)

btn_return = tk.Button(frame, text="Return Book", width=15, command=return_book, bg="#F44336", fg="white")
btn_return.grid(row=1, column=1, padx=10, pady=10)

btn_search = tk.Button(frame, text="Search Book", width=15, command=search_book, bg="#FF9800", fg="white")
btn_search.grid(row=2, column=0, padx=10, pady=10)

btn_exit = tk.Button(frame, text="Exit", width=15, command=root.quit, bg="#607D8B", fg="white")
btn_exit.grid(row=2, column=1, padx=10, pady=10)

listbox = tk.Listbox(root, width=80)
listbox.pack(pady=20)

# scrollbar = tk.Scrollbar(frame)
# scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# listbox = tk.Listbox(frame, width=100, yscrollcommand=scrollbar.set, font=("Consolas", 12))
# listbox.pack()

# scrollbar.config(command=listbox.yview)

# Start the GUI event loop
display_books()

root.mainloop()