# Library imports
import streamlit as st
import mysql.connector
from datetime import date
import pandas as pd

# --- Database Connection ---
def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Password123",  # Replace with your MySQL password
            database="library_db"
        )
        return db
    except mysql.connector.Error as err:
        st.error(f"Error connecting to database: {err}")
        return None

def setup_database(db):
    """Creates the necessary tables if they don't already exist."""
    cursor = db.cursor()
    cursor.execute("USE library_db")
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
    cursor.close()

# --- Core Functions ---
def display_books(db):
    """Fetches and displays all books in a DataFrame."""
    cursor = db.cursor()
    cursor.execute("SELECT book_id, title, author, available FROM books")
    result = cursor.fetchall()
    cursor.close()
    if result:
        df = pd.DataFrame(result, columns=['ID', 'Title', 'Author', 'Available'])
        df['Status'] = df['Available'].apply(lambda x: "Available" if x else "Borrowed")
        st.dataframe(df[['ID', 'Title', 'Author', 'Status']])
    else:
        st.info("No books found in the library.")

def add_book(db, title, author):
    """Adds a new book to the database."""
    if title and author:
        cursor = db.cursor()
        cursor.execute("INSERT INTO books (title, author) VALUES (%s, %s)", (title, author))
        db.commit()
        cursor.close()
        st.success("Book added successfully!")
    else:
        st.warning("Title and Author cannot be empty.")

def borrow_book(db, book_id):
    """Borrows a book by its ID."""
    if book_id:
        cursor = db.cursor()
        cursor.execute("SELECT available FROM books WHERE book_id = %s", (book_id,))
        result = cursor.fetchone()
        if result and result[0]:
            cursor.execute("UPDATE books SET available = FALSE WHERE book_id = %s", (book_id,))
            cursor.execute("INSERT INTO borrow (book_id, borrow_date) VALUES (%s, %s)", (book_id, date.today()))
            db.commit()
            st.success("Book borrowed successfully!")
        else:
            st.warning("Book is not available for borrowing.")
        cursor.close()
    else:
        st.warning("Book ID cannot be empty.")

def return_book(db, book_id):
    """Returns a borrowed book by its ID."""
    if book_id:
        cursor = db.cursor()
        cursor.execute("SELECT available FROM books WHERE book_id = %s", (book_id,))
        result = cursor.fetchone()
        if result and not result[0]:
            cursor.execute("UPDATE books SET available = TRUE WHERE book_id = %s", (book_id,))
            cursor.execute("UPDATE borrow SET return_date = %s WHERE book_id = %s AND return_date IS NULL", (date.today(), book_id))
            db.commit()
            st.success("Book returned successfully!")
        else:
            st.error("Book is not currently borrowed.")
        cursor.close()
    else:
        st.warning("Book ID cannot be empty.")

def search_book(db, search_term):
    """Searches for books by title or author."""
    if search_term:
        cursor = db.cursor()
        query = "SELECT book_id, title, author, available FROM books WHERE title LIKE %s OR author LIKE %s"
        cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        results = cursor.fetchall()
        cursor.close()
        if results:
            df = pd.DataFrame(results, columns=['ID', 'Title', 'Author', 'Available'])
            df['Status'] = df['Available'].apply(lambda x: "Available" if x else "Borrowed")
            st.write("### Search Results")
            st.dataframe(df[['ID', 'Title', 'Author', 'Status']])
        else:
            st.info("No books found matching the search criteria.")
    else:
        st.warning("Search term cannot be empty.")


# --- Streamlit UI ---
st.set_page_config(page_title="Library Management System", layout="wide")
st.title("Library Management System")

db = get_db_connection()

if db:
    setup_database(db)

    st.sidebar.title("Actions")
    menu = ["Display Books", "Add Book", "Borrow Book", "Return Book", "Search Book"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Display Books":
        st.header("All Books")
        display_books(db)

    elif choice == "Add Book":
        st.header("Add a New Book")
        with st.form("add_book_form"):
            title = st.text_input("Title")
            author = st.text_input("Author")
            submitted = st.form_submit_button("Add Book")
            if submitted:
                add_book(db, title, author)
                st.experimental_rerun()

    elif choice == "Borrow Book":
        st.header("Borrow a Book")
        with st.form("borrow_book_form"):
            book_id = st.number_input("Book ID to Borrow", min_value=1, step=1)
            submitted = st.form_submit_button("Borrow Book")
            if submitted:
                borrow_book(db, book_id)
                st.experimental_rerun()
        st.info("Refer to the 'Display Books' section to find the ID of the book you want to borrow.")


    elif choice == "Return Book":
        st.header("Return a Book")
        with st.form("return_book_form"):
            book_id = st.number_input("Book ID to Return", min_value=1, step=1)
            submitted = st.form_submit_button("Return Book")
            if submitted:
                return_book(db, book_id)
                st.experimental_rerun()
        st.info("Refer to the 'Display Books' section to find the ID of the book you are returning.")


    elif choice == "Search Book":
        st.header("Search for a Book")
        search_term = st.text_input("Enter book title or author")
        if st.button("Search"):
            search_book(db, search_term)

    db.close()
else:
    st.error("Cannot connect to the database. Please check your connection and credentials.")