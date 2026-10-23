
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Create a database to store movies
connection = sqlite3.connect("reelvault.db")
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        genre TEXT,
        rating REAL DEFAULT 0,
        watched INTEGER DEFAULT 0
    )
""")
connection.commit()


# Add a movie to the database
def add_movie():
    title = title_entry.get().strip()
    genre = genre_entry.get().strip()
    rating_text = rating_entry.get().strip()

    if not title:
        messagebox.showerror("Error", "Please enter a movie title.")
        return

    try:
        rating = float(rating_text) if rating_text else 0
        if not 0 <= rating <= 10:
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Rating must be between 0 and 10.")
        return

    cursor.execute(
        "INSERT INTO movies (title, genre, rating) VALUES (?, ?, ?)",
        (title, genre, rating)
    )
    connection.commit()

    title_entry.delete(0, tk.END)
    genre_entry.delete(0, tk.END)
    rating_entry.delete(0, tk.END)

    refresh_movies()


# Display movies in the list
def refresh_movies():
    for item in movie_table.get_children():
        movie_table.delete(item)

    cursor.execute(
        "SELECT id, title, genre, rating, watched FROM movies ORDER BY id DESC"
    )

    for movie in cursor.fetchall():
        movie_id, title, genre, rating, watched = movie
        status = "Watched" if watched else "Not watched"

        movie_table.insert(
            "",
            tk.END,
            values=(movie_id, title, genre, f"{rating:.1f}/10", status)
        )


# Mark a movie as watched or unwatched
def toggle_watched():
    selected = movie_table.selection()

    if not selected:
        messagebox.showwarning("Select a movie", "Choose a movie first.")
        return

    movie = movie_table.item(selected[0], "values")
    movie_id = movie[0]

    cursor.execute("SELECT watched FROM movies WHERE id = ?", (movie_id,))
    current_status = cursor.fetchone()[0]

    cursor.execute(
        "UPDATE movies SET watched = ? WHERE id = ?",
        (0 if current_status else 1, movie_id)
    )
    connection.commit()

    refresh_movies()


# Delete a movie
def delete_movie():
    selected = movie_table.selection()

    if not selected:
        messagebox.showwarning("Select a movie", "Choose a movie first.")
        return

    movie = movie_table.item(selected[0], "values")
    movie_id = movie[0]

    confirm = messagebox.askyesno(
        "Confirm deletion",
        "Are you sure you want to delete this movie?"
    )

    if confirm:
        cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
        connection.commit()
        refresh_movies()


# Close the app and database safely
def close_app():
    connection.close()
    root.destroy()


# Create the application window
root = tk.Tk()
root.title("ReelVault - Movie Watchlist")
root.geometry("850x550")
root.minsize(700, 450)
root.configure(bg="#151515")

# Theme and styles
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Treeview",
    background="#242424",
    foreground="white",
    fieldbackground="#242424",
    rowheight=30
)
style.configure(
    "Treeview.Heading",
    background="#383838",
    foreground="white",
    font=("Arial", 10, "bold")
)
style.map("Treeview", background=[("selected", "#7048E8")])

# Header
header = tk.Label(
    root,
    text="REELVAULT",
    font=("Arial", 25, "bold"),
    bg="#151515",
    fg="#A78BFA"
)
header.pack(pady=(18, 2))

subtitle = tk.Label(
    root,
    text="Your personal movie collection",
    font=("Arial", 11),
    bg="#151515",
    fg="#BBBBBB"
)
subtitle.pack(pady=(0, 18))

# Input section
form = tk.Frame(root, bg="#202020", padx=12, pady=12)
form.pack(fill="x", padx=20, pady=5)

tk.Label(form, text="Movie title", bg="#202020", fg="white").grid(
    row=0, column=0, sticky="w", padx=5
)
tk.Label(form, text="Genre", bg="#202020", fg="white").grid(
    row=0, column=1, sticky="w", padx=5
)
tk.Label(form, text="Rating / 10", bg="#202020", fg="white").grid(
    row=0, column=2, sticky="w", padx=5
)

title_entry = tk.Entry(form, width=25)
title_entry.grid(row=1, column=0, padx=5, pady=7, sticky="ew")

genre_entry = tk.Entry(form, width=18)
genre_entry.grid(row=1, column=1, padx=5, pady=7, sticky="ew")

rating_entry = tk.Entry(form, width=10)
rating_entry.grid(row=1, column=2, padx=5, pady=7, sticky="ew")

add_button = tk.Button(
    form,
    text="Add Movie",
    command=add_movie,
    bg="#7048E8",
    fg="white",
    activebackground="#5B36C9",
    activeforeground="white",
    relief="flat",
    padx=12,
    pady=5
)
add_button.grid(row=1, column=3, padx=8)

form.columnconfigure(0, weight=3)
form.columnconfigure(1, weight=2)

# Movie table
table_frame = tk.Frame(root, bg="#151515")
table_frame.pack(fill="both", expand=True, padx=20, pady=12)

columns = ("id", "title", "genre", "rating", "status")
movie_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings",
    selectmode="browse"
)

movie_table.heading("id", text="ID")
movie_table.heading("title", text="MOVIE")
movie_table.heading("genre", text="GENRE")
movie_table.heading("rating", text="RATING")
movie_table.heading("status", text="STATUS")

movie_table.column("id", width=45, anchor="center")
movie_table.column("title", width=280)
movie_table.column("genre", width=150)
movie_table.column("rating", width=100, anchor="center")
movie_table.column("status", width=130, anchor="center")

scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=movie_table.yview
)
movie_table.configure(yscrollcommand=scrollbar.set)

movie_table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Action buttons
actions = tk.Frame(root, bg="#151515")
actions.pack(pady=(0, 18))

tk.Button(
    actions,
    text="Toggle Watched",
    command=toggle_watched,
    bg="#333333",
    fg="white",
    relief="flat",
    padx=15,
    pady=8
).pack(side="left", padx=6)

tk.Button(
    actions,
    text="Delete Selected",
    command=delete_movie,
    bg="#8B3030",
    fg="white",
    relief="flat",
    padx=15,
    pady=8
).pack(side="left", padx=6)

refresh_movies()
root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
