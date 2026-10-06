import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import timedelta
import libcore

# (settings key, label, max allowed value or 0 for unlimited)
FIELDS = [
    ("max_copy", "Maximum Copies", 0),
    ("due_days", "Borrow Days", 365),
    ("max_title", "Max Title Length", 0),
    ("max_author", "Max Author Length", 0),
    ("initial_fine", "Initial Fine (PHP)", 0),
    ("missed_fine", "Missed Days Fine (PHP)", 0),
    ("max_borrow", "Max Borrow", 0),
    ("compensation_fee", "Compensation Fee (PHP)", 0),
]


class LibSys:
    def __init__(self, root):
        self.root = root
        self.root.title("New Archive Zealous Indexers Library")
        self.root.geometry("1150x740")
        self.root.minsize(1000, 660)

        style = ttk.Style()

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Treeview", rowheight=24)
        style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Brand.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure(
            "Sidebar.TButton", anchor="w", padding=(10, 9), font=("Segoe UI", 10)
        )
        style.configure(
            "SidebarActive.TButton",
            anchor="w",
            padding=(10, 9),
            font=("Segoe UI", 10, "bold"),
        )

        self.role = None
        self.username = None
        self.attempts = 0

        self.nav_buttons = {}
        self.pages = {}
        self.nav_items = []
        self.content_frame = None
        self.current_page = None

        self.root_container = ttk.Frame(root)
        self.root_container.pack(fill="both", expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.confirm_exit)
        self.show_login()

    def clear_root(self):
        for child in self.root_container.winfo_children():
            child.destroy()

    def page_header(self, title, subtitle=None, refresh=False):
        header = ttk.Frame(self.content_frame)
        header.pack(fill="x", pady=(0, 8))

        ttk.Label(header, text=title, style="Title.TLabel").pack(side="left")
        if subtitle:
            ttk.Label(header, text=subtitle, style="Sub.TLabel").pack(
                side="left", padx=(12, 0)
            )
        if refresh:
            ttk.Button(header, text="Refresh", command=self.refresh_current_page).pack(
                side="right"
            )

        ttk.Separator(self.content_frame).pack(fill="x", pady=(0, 12))

    def build_tree(self, parent, columns, widths=None, height=14, selectmode="browse"):
        holder = ttk.Frame(parent)
        tree = ttk.Treeview(
            holder,
            columns=columns,
            show="headings",
            height=height,
            selectmode=selectmode,
        )

        for col in columns:
            tree.heading(col, text=col)
            tree.column(
                col, width=(widths or {}).get(col, 120), anchor="w", stretch=True
            )

        visible = ttk.Scrollbar(holder, orient="vertical", command=tree.yview)

        tree.configure(yscrollcommand=visible.set)
        tree.pack(side="left", fill="both", expand=True)
        visible.pack(side="right", fill="y")
        return holder, tree

    def form_row(self, parent, row, label, widget):
        ttk.Label(parent, text=label).grid(
            row=row, column=0, sticky="w", padx=(0, 10), pady=6
        )
        widget.grid(row=row, column=1, sticky="ew", pady=6)

    def form_hint(self, parent, row, text):
        ttk.Label(parent, text=text, style="Sub.TLabel").grid(
            row=row, column=1, sticky="w", pady=(0, 6)
        )

    def confirm_exit(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

    def show_login(self):
        self.clear_root()
        self.role = None
        self.username = None
        self.attempts = 0
        self.nav_buttons = {}
        self.content_frame = None
        self.current_page = None

        wrap = ttk.Frame(self.root_container, padding=20)
        wrap.place(relx=0.5, rely=0.45, anchor="center")

        card = ttk.LabelFrame(wrap, padding=24)
        card.grid(row=0, column=0)
        card.columnconfigure(0, weight=1)

        ttk.Label(
            card, text="New Archive Zealous Indexers Library", style="Title.TLabel"
        ).grid(row=0, column=0, columnspan=2, pady=(0, 4))
        ttk.Label(card, text="Library Management System", style="Sub.TLabel").grid(
            row=1, column=0, columnspan=2, pady=(0, 20)
        )
        ttk.Separator(card).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(0, 16)
        )

        self.login_user = ttk.Entry(card, width=32)
        self.login_pass = ttk.Entry(card, width=32, show="*")

        self.form_row(card, 3, "Username", self.login_user)
        self.form_row(card, 4, "Password", self.login_pass)

        self.login_msg = ttk.Label(card, text="", foreground="red")
        self.login_msg.grid(row=5, column=0, columnspan=2, pady=(10, 0))

        btns = ttk.Frame(card)
        btns.grid(row=6, column=0, columnspan=2, pady=(18, 0))
        ttk.Button(btns, text="Login", command=self.do_login).pack(side="left", padx=6)
        ttk.Button(btns, text="Exit", command=self.confirm_exit).pack(
            side="left", padx=6
        )

        self.login_user.bind("<Return>", lambda e: self.login_pass.focus_set())
        self.login_pass.bind("<Return>", lambda e: self.do_login())
        self.login_user.focus_set()

    def do_login(self):
        username = self.login_user.get().strip()
        password = self.login_pass.get().strip()

        if username not in libcore.users:
            self.fail_login("Invalid credentials.")
            return
        if libcore.users[username]["password"] != password:
            self.fail_login("Invalid password.")
            return

        self.username = username
        self.role = libcore.users[username]["role"]
        self.attempts = 0
        messagebox.showinfo("Login", f"Login successful. Welcome, {username}.")
        self.show_app()

    def fail_login(self, msg):
        self.attempts += 1
        remaining = 3 - self.attempts
        self.login_pass.delete(0, "end")
        if remaining <= 0:
            messagebox.showerror("Login", "Too many failed attempts. Exiting.")
            self.root.destroy()
            return
        self.login_msg.config(text=f"{msg} {remaining} attempt(s) remaining.")

    def show_app(self):
        self.clear_root()

        self.nav_items = self.get_nav_items()
        self.pages = self.get_pages()
        self.nav_buttons = {}

        sidebar = ttk.Frame(self.root_container, width=225, padding=(14, 16))
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ttk.Label(sidebar, text="NAZI Library", style="Brand.TLabel").pack(anchor="w")
        ttk.Label(sidebar, text=f"{self.role}", style="Sub.TLabel").pack(
            anchor="w", pady=(2, 14)
        )
        ttk.Separator(sidebar).pack(fill="x", pady=(0, 10))

        for key, label in self.nav_items:
            btn = ttk.Button(
                sidebar,
                text=label,
                style="Sidebar.TButton",
                command=lambda k=key: self.navigate(k),
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[key] = btn

        ttk.Button(sidebar, text="Logout", command=self.logout).pack(
            side="bottom", fill="x", pady=(8, 0)
        )
        ttk.Separator(sidebar).pack(side="bottom", fill="x", pady=(10, 8))

        ttk.Separator(self.root_container, orient="vertical").pack(
            side="left", fill="y"
        )

        self.content_frame = ttk.Frame(self.root_container, padding=18)
        self.content_frame.pack(side="left", fill="both", expand=True)

        self.navigate(self.nav_items[0][0])

    def get_nav_items(self):
        if self.role == "Administrator":
            return [
                ("books", "View Books"),
                ("members", "View Members"),
                ("search_members", "Search Members"),
                ("deactivated", "Deactivated Members"),
                ("users", "Manage Users"),
                ("settings", "Manage Settings"),
                ("remove_book", "Remove Book"),
                ("deactivate_member", "Deactivate Member"),
            ]
        return [
            ("add_book", "Add Book"),
            ("add_member", "Add Member"),
            ("members", "View Members"),
            ("search_members", "Search Members"),
            ("books", "View Books"),
            ("search_books", "Search Books"),
            ("borrow", "Borrow Book"),
            ("return", "Return Book"),
        ]

    def get_pages(self):
        if self.role == "Administrator":
            return {
                "books": self.page_books,
                "members": self.page_members,
                "search_members": self.page_search_members,
                "deactivated": self.page_deactivated,
                "users": self.page_users,
                "settings": self.page_settings,
                "remove_book": self.page_remove_book,
                "deactivate_member": self.page_deactivate_member,
            }
        return {
            "add_book": self.page_add_book,
            "add_member": self.page_add_member,
            "members": self.page_members,
            "search_members": self.page_search_members,
            "books": self.page_books,
            "search_books": self.page_search_books,
            "borrow": self.page_borrow,
            "return": self.page_return,
        }

    def navigate(self, key):
        if key not in self.pages or self.content_frame is None:
            return
        for child in self.content_frame.winfo_children():
            child.destroy()
        self.current_page = key
        for k, btn in self.nav_buttons.items():
            btn.configure(
                style="SidebarActive.TButton" if k == key else "Sidebar.TButton"
            )
        self.pages[key]()

    def refresh_current_page(self):
        if self.current_page:
            self.navigate(self.current_page)

    def logout(self):
        if not messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            return
        self.show_login()

    def page_books(self):
        self.page_header("View Books", refresh=True)
        nb = ttk.Notebook(self.content_frame)
        nb.pack(fill="both", expand=True)

        self._tab_available(nb)
        self._tab_borrowed(nb)
        self._tab_dead(nb)
        self._tab_returned(nb)

    def _tab_available(self, nb):
        tab = ttk.Frame(nb, padding=8)
        nb.add(tab, text="Available")
        cols = ("BookID", "Title", "Author", "Genre", "On Shelf")
        holder, tree = self.build_tree(
            tab,
            cols,
            {"BookID": 90, "Title": 280, "Author": 190, "Genre": 150, "On Shelf": 90},
        )
        holder.pack(fill="both", expand=True)

        for b in sorted(
            [x for x in libcore.on_books if x["copy"] > 0], key=lambda x: x["BookID"]
        ):
            tree.insert(
                "",
                "end",
                values=(
                    b["BookID"],
                    b["title"],
                    b["author"],
                    b.get("genre", ""),
                    b["copy"],
                ),
            )

    def _tab_borrowed(self, nb):
        tab = ttk.Frame(nb, padding=8)
        nb.add(tab, text="Borrowed")
        cols = (
            "BookID",
            "Title",
            "MemberID",
            "Borrower",
            "Contact",
            "Borrowed",
            "Due",
            "Status",
        )
        holder, tree = self.build_tree(
            tab,
            cols,
            {
                "BookID": 80,
                "Title": 200,
                "MemberID": 85,
                "Borrower": 160,
                "Contact": 110,
                "Borrowed": 130,
                "Due": 130,
                "Status": 150,
            },
        )
        holder.pack(fill="both", expand=True)

        current = libcore.now()
        for r in sorted(libcore.off_books, key=lambda x: x["BookID"]):
            due = libcore.to_date(r["due"])
            status = (
                f"OVERDUE by {(current.date() - due.date()).days} day(s)"
                if current > due
                else "On time"
            )
            tree.insert(
                "",
                "end",
                values=(
                    r["BookID"],
                    r["title"],
                    r["MemberID"],
                    r.get("borrower", ""),
                    r.get("contact", ""),
                    libcore.format_date(r["borrowed"]),
                    due.strftime("%Y-%m-%d"),
                    status,
                ),
            )

        bar = ttk.Frame(tab)
        bar.pack(fill="x", pady=(8, 0))
        ttk.Button(
            bar, text="Extend Due Date", command=lambda: self.extend_due(tree)
        ).pack(side="right")

    def _tab_dead(self, nb):
        tab = ttk.Frame(nb, padding=8)
        nb.add(tab, text="Unavailable (Lost / Damaged)")
        cols = (
            "BookID",
            "Title",
            "MemberID",
            "Borrower",
            "Status",
            "Fee",
            "Payment",
            "Logged",
        )
        holder, tree = self.build_tree(
            tab,
            cols,
            {
                "BookID": 80,
                "Title": 200,
                "MemberID": 85,
                "Borrower": 150,
                "Status": 100,
                "Fee": 90,
                "Payment": 100,
                "Logged": 140,
            },
        )
        holder.pack(fill="both", expand=True)

        for r in sorted(libcore.dead_books, key=lambda x: x["BookID"]):
            tree.insert(
                "",
                "end",
                values=(
                    r["BookID"],
                    r.get("title", ""),
                    r["MemberID"],
                    r.get("borrower", ""),
                    r.get("status", ""),
                    f"PHP {r.get('fee', libcore.settings['compensation_fee'])}",
                    "PAID" if r.get("paid") else "NOT PAID",
                    libcore.format_date(r["logged"]) if r.get("logged") else "Unknown",
                ),
            )

        bar = ttk.Frame(tab)
        bar.pack(fill="x", pady=(8, 0))
        ttk.Button(
            bar, text="Update Payment Status", command=lambda: self.update_payment(tree)
        ).pack(side="right")

    def _tab_returned(self, nb):
        tab = ttk.Frame(nb, padding=8)
        nb.add(tab, text="Returned")
        cols = (
            "BookID",
            "Title",
            "MemberID",
            "Borrower",
            "Borrowed",
            "Due",
            "Returned",
        )
        holder, tree = self.build_tree(
            tab,
            cols,
            {
                "BookID": 80,
                "Title": 220,
                "MemberID": 85,
                "Borrower": 160,
                "Borrowed": 130,
                "Due": 130,
                "Returned": 130,
            },
        )
        holder.pack(fill="both", expand=True)

        for r in libcore.returned_books:
            tree.insert(
                "",
                "end",
                values=(
                    r["BookID"],
                    r.get("title", ""),
                    r["MemberID"],
                    r.get("borrower", ""),
                    libcore.format_date(r["borrowed"]),
                    libcore.format_date(r["due"]),
                    libcore.format_date(r["returned"]),
                ),
            )

    def extend_due(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Extend", "Select a borrowed book first.")
            return

        values = tree.item(sel[0], "values")
        book_id, member_id = values[0], values[2]

        record = libcore.find_off(book_id, member_id)
        if not record:
            messagebox.showerror("Extend", "Borrow record not found.")
            self.refresh_current_page()
            return

        due = libcore.to_date(record["due"])
        if libcore.now() > due:
            late = (libcore.now().date() - due.date()).days
            fine = (
                libcore.settings["initial_fine"]
                + late * libcore.settings["missed_fine"]
            )
            messagebox.showerror(
                "Extend",
                f"This book is OVERDUE by {late} day(s).\n"
                f"Fine: PHP {fine}\n\nOverdue books cannot be extended.",
            )
            return

        extra = simpledialog.askinteger(
            "Extend Due Date",
            "Extend by how many days?",
            parent=self.root,
            minvalue=1,
            maxvalue=365,
        )
        if extra is None:
            return

        new_due = due + timedelta(days=extra)
        record["due"] = libcore.to_string(new_due)
        libcore.save_db()
        messagebox.showinfo("Extend", f"New due date: {new_due.strftime('%Y-%m-%d')}")
        self.refresh_current_page()

    def update_payment(self, tree):
        sel = tree.selection()
        if not sel:
            messagebox.showwarning("Payment", "Select an unavailable book first.")
            return

        values = tree.item(sel[0], "values")
        book_id, member_id = values[0], values[2]

        record = libcore.find_dead(book_id, member_id)
        if not record:
            messagebox.showerror("Payment", "Record not found.")
            self.refresh_current_page()
            return
        if record.get("paid"):
            messagebox.showinfo("Payment", "This record is already paid.")
            return

        fee = record.get("fee", libcore.settings["compensation_fee"])
        if not messagebox.askyesno(
            "Payment",
            f"Mark this record as PAID?\n\n"
            f"BookID:   {record['BookID']}\n"
            f"MemberID: {record['MemberID']}\n"
            f"Status:   {record.get('status')}\n"
            f"Fee:      PHP {fee}",
        ):
            return

        record["paid"] = True
        libcore.save_db()
        messagebox.showinfo("Payment", "Payment status updated to: Paid")
        self.refresh_current_page()

    def page_members(self):
        self.page_header("Current Members", refresh=True)

        active = [m for m in libcore.members if m.get("active", True)]
        if not active:
            ttk.Label(self.content_frame, text="No registered members.").pack(pady=20)
            return

        cols = ("MemberID", "Name", "Contact", "Books Borrowed")
        holder, tree = self.build_tree(
            self.content_frame,
            cols,
            {"MemberID": 120, "Name": 320, "Contact": 180, "Books Borrowed": 160},
            height=18,
        )
        holder.pack(fill="both", expand=True)

        for m in sorted(active, key=lambda x: x["MemberID"]):
            count = sum(1 for r in libcore.off_books if r["MemberID"] == m["MemberID"])
            tree.insert(
                "",
                "end",
                values=(
                    m["MemberID"],
                    f"{m['first_name']} {m['last_name']}",
                    m["contact"],
                    count,
                ),
            )

    def page_deactivated(self):
        self.page_header("Deactivated Members", refresh=True)

        deactivated = [m for m in libcore.members if not m.get("active", True)]
        if not deactivated:
            ttk.Label(self.content_frame, text="No deactivated members.").pack(pady=20)
            return

        cols = ("MemberID", "Name", "Contact", "Deactivated")
        holder, tree = self.build_tree(
            self.content_frame,
            cols,
            {"MemberID": 120, "Name": 320, "Contact": 180, "Deactivated": 200},
            height=18,
        )
        holder.pack(fill="both", expand=True)

        for m in sorted(deactivated, key=lambda x: x["MemberID"]):
            date = (
                libcore.format_date(m["deactivated"])
                if m.get("deactivated")
                else "Unknown"
            )
            tree.insert(
                "",
                "end",
                values=(
                    m["MemberID"],
                    f"{m['first_name']} {m['last_name']}",
                    m["contact"],
                    date,
                ),
            )

    def page_search_members(self):
        self.page_header("Search Members")

        top = ttk.Frame(self.content_frame)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Search by name, contact, or MemberID:").pack(side="left")
        self.search_member_entry = ttk.Entry(top, width=42)
        self.search_member_entry.pack(side="left", padx=8)
        self.search_member_entry.bind("<Return>", lambda e: self.do_search_members())
        ttk.Button(top, text="Search", command=self.do_search_members).pack(side="left")

        cols = ("MemberID", "Name", "Contact", "Currently Borrowing")
        holder, self.search_member_tree = self.build_tree(
            self.content_frame,
            cols,
            {"MemberID": 100, "Name": 240, "Contact": 150, "Currently Borrowing": 430},
            height=18,
        )
        holder.pack(fill="both", expand=True)

        self.search_member_entry.focus_set()

    def do_search_members(self):
        query = self.search_member_entry.get().strip().lower()
        if not query:
            messagebox.showwarning("Search", "Search query cannot be empty.")
            return

        self.search_member_tree.delete(*self.search_member_tree.get_children())
        found = 0

        for member in libcore.members:
            if not member.get("active", True):
                continue
            fullname = f"{member['first_name']} {member['last_name']}".lower()
            if (
                query in fullname
                or query in member["contact"].lower()
                or query in member["MemberID"].lower()
            ):
                borrowed = [
                    r for r in libcore.off_books if r["MemberID"] == member["MemberID"]
                ]
                if borrowed:
                    parts = []
                    for r in borrowed:
                        due = libcore.to_date(r["due"])
                        if libcore.now() > due:
                            late = (libcore.now().date() - due.date()).days
                            parts.append(
                                f"{r['BookID']}: {r['title']} (OVERDUE {late}d)"
                            )
                        else:
                            parts.append(
                                f"{r['BookID']}: {r['title']} "
                                f"(Due {due.strftime('%Y-%m-%d')})"
                            )
                    detail = "; ".join(parts)
                else:
                    detail = "None"

                self.search_member_tree.insert(
                    "",
                    "end",
                    values=(
                        member["MemberID"],
                        f"{member['first_name']} {member['last_name']}",
                        member["contact"],
                        detail,
                    ),
                )
                found += 1

        if found == 0:
            messagebox.showinfo("Search", f"No matching members found for '{query}'.")

    def page_search_books(self):
        self.page_header("Search Books")

        top = ttk.Frame(self.content_frame)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Search by title, author, genre, or BookID:").pack(
            side="left"
        )
        self.search_book_entry = ttk.Entry(top, width=42)
        self.search_book_entry.pack(side="left", padx=8)
        self.search_book_entry.bind("<Return>", lambda e: self.do_search_books())
        ttk.Button(top, text="Search", command=self.do_search_books).pack(side="left")

        cols = ("Status", "BookID", "Title", "Author", "Genre", "Details")
        holder, self.search_book_tree = self.build_tree(
            self.content_frame,
            cols,
            {
                "Status": 100,
                "BookID": 80,
                "Title": 240,
                "Author": 170,
                "Genre": 130,
                "Details": 240,
            },
            height=18,
        )
        holder.pack(fill="both", expand=True)

        self.search_book_entry.focus_set()

    def do_search_books(self):
        query = self.search_book_entry.get().strip().lower()
        if not query:
            messagebox.showwarning("Search", "Search query cannot be empty.")
            return

        self.search_book_tree.delete(*self.search_book_tree.get_children())
        found = 0

        for book in libcore.on_books:
            if (
                query in book["title"].lower()
                or query in book["author"].lower()
                or query in book.get("genre", "").lower()
                or query in book["BookID"].lower()
            ):
                status = "Available" if book["copy"] > 0 else "Unavailable"
                details = f"Copies on shelf: {book['copy']}"
                self.search_book_tree.insert(
                    "",
                    "end",
                    values=(
                        status,
                        book["BookID"],
                        book["title"],
                        book["author"],
                        book.get("genre", ""),
                        details,
                    ),
                )
                found += 1

        for record in libcore.off_books:
            if (
                query in record["title"].lower()
                or query in record["author"].lower()
                or query in record.get("genre", "").lower()
                or query in record["BookID"].lower()
            ):
                details = (
                    f"{record.get('borrower', '')} | "
                    f"Due {libcore.format_date(record['due'])}"
                )
                self.search_book_tree.insert(
                    "",
                    "end",
                    values=(
                        "Borrowed",
                        record["BookID"],
                        record["title"],
                        record["author"],
                        record.get("genre", ""),
                        details,
                    ),
                )
                found += 1

        if found == 0:
            messagebox.showinfo("Search", f"No matching books found for '{query}'.")

    def page_add_book(self):
        self.page_header("Add Book")

        form = ttk.Frame(self.content_frame)
        form.pack(anchor="nw", pady=6)
        form.columnconfigure(1, weight=1)

        self.ab_title = ttk.Entry(form, width=46)
        self.ab_author = ttk.Entry(form, width=46)
        self.ab_genre = ttk.Entry(form, width=46)
        self.ab_copies = ttk.Entry(form, width=46)

        self.form_row(form, 0, "Book title", self.ab_title)
        self.form_row(form, 1, "Author", self.ab_author)
        self.form_row(form, 2, "Genre", self.ab_genre)
        self.form_row(form, 3, "Number of copies", self.ab_copies)

        bar = ttk.Frame(self.content_frame)
        bar.pack(anchor="w", pady=14)
        ttk.Button(bar, text="Add Book", command=self.submit_add_book).pack(side="left")
        ttk.Button(bar, text="Clear", command=self.refresh_current_page).pack(
            side="left", padx=8
        )

        self.ab_title.focus_set()

    @staticmethod
    def validate_title(title):
        s = libcore.settings
        if not title:
            return "Book title cannot be empty."
        if len(title) > s["max_title"]:
            return f"Book title is too long. Maximum is {s['max_title']} characters."
        if title.isdigit() and len(title) >= 5:
            return "Invalid title."
        if not all(ch.isalnum() or ch in " .!?,;:-'&" for ch in title):
            return "Invalid title."
        if any(ch * 3 in title for ch in ".!?,;:-'&"):
            return "Invalid title."
        if libcore.rep_checker(title):
            return "Invalid book title."
        return None

    @staticmethod
    def validate_author(author):
        s = libcore.settings
        if not author:
            return "Author name cannot be empty."
        if len(author) > s["max_author"]:
            return f"Author name is too long. Maximum is {s['max_author']} characters."
        if author.isdigit():
            return "Invalid author name."
        if not all(ch.isalpha() or ch in " .'-" for ch in author):
            return (
                "Invalid author. Only letters, spaces, periods, hyphens, "
                "and apostrophes are allowed."
            )
        if any(ch * 3 in author for ch in ".'-"):
            return "Invalid author name."
        if libcore.rep_checker(author):
            return "Invalid author name."
        return None

    @staticmethod
    def validate_genre(genre):
        if not genre:
            return "Book genre cannot be empty."
        if len(genre) > 20:
            return "Book genre is too long."
        if not all(ch.isalnum() or ch in " -" for ch in genre):
            return "Invalid genre."
        if libcore.rep_checker(genre):
            return "Invalid book genre."
        return None

    def submit_add_book(self):
        title = " ".join(self.ab_title.get().split())
        author = " ".join(self.ab_author.get().split())
        genre = " ".join(self.ab_genre.get().split())

        err = (
            self.validate_title(title)
            or self.validate_author(author)
            or self.validate_genre(genre)
        )
        if err:
            messagebox.showerror("Add Book", err)
            return

        try:
            copies = int(self.ab_copies.get().strip())
        except ValueError:
            messagebox.showerror("Add Book", "Invalid number of copies.")
            return

        if copies <= 0:
            messagebox.showerror("Add Book", "Please enter a valid book quantity.")
            return
        if copies > libcore.settings["max_copy"]:
            messagebox.showerror("Add Book", "Amount exceeds maximum inventory.")
            return

        existing = libcore.find_record(title, author, genre)
        if existing:
            self._add_to_existing(existing, title, author, genre, copies)
            return

        tdupe, adupe = title.lower(), author.lower()
        all_books = (
            libcore.on_books
            + libcore.off_books
            + libcore.returned_books
            + libcore.dead_books
        )

        for record in all_books:
            same_title = record.get("title", "").strip().lower() == tdupe
            same_author = record.get("author", "").strip().lower() == adupe
            diff_genre = record.get("genre", "").strip().lower() != genre.lower()
            if same_title and same_author and diff_genre:
                gdupe = record.get("genre", "Not specified")
                if messagebox.askyesno(
                    "Add Book",
                    f"A book with the same title and author already exists "
                    f"with genre: {gdupe}\n\nDid you mean {gdupe}?",
                ):
                    existing2 = libcore.find_record(title, author, gdupe)
                    if existing2:
                        self._add_to_existing(existing2, title, author, gdupe, copies)
                        return
                break

        if not messagebox.askyesno(
            "Add Book",
            f"Add this new book?\n\nTitle: {title}\nAuthor: {author}\n"
            f"Genre: {genre}\nCopies: {copies}",
        ):
            return

        book_id = libcore.get_BID()
        libcore.on_books.append(
            {
                "BookID": book_id,
                "title": title,
                "author": author,
                "genre": genre,
                "copy": copies,
            }
        )
        libcore.save_db()

        messagebox.showinfo(
            "Add Book",
            f"Book added successfully.\n\nBookID: {book_id}\nTitle: {title}\n"
            f"Author: {author}\nGenre: {genre}\nCopies: {copies}",
        )
        self.refresh_current_page()

    def _add_to_existing(self, existing, title, author, genre, copies):
        book_id = existing["BookID"]
        available = libcore.find_book(book_id)

        if available:
            if available["copy"] + copies > libcore.settings["max_copy"]:
                messagebox.showerror(
                    "Add Book",
                    f"Cannot add that many copies. Maximum inventory is "
                    f"{libcore.settings['max_copy']} copies.",
                )
                return
            if not messagebox.askyesno(
                "Add Book", f"Add {copies} copies to existing BookID {book_id}?"
            ):
                return
            available["copy"] += copies
        else:
            if not messagebox.askyesno(
                "Add Book",
                f"This book exists in records but is not on the shelf.\n\n"
                f"Add a new on-shelf entry for BookID {book_id}?",
            ):
                return
            libcore.on_books.append(
                {
                    "BookID": book_id,
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "copy": copies,
                }
            )

        libcore.save_db()
        messagebox.showinfo(
            "Add Book",
            f"Inventory updated for BookID: {book_id}\nAdded copies: {copies}",
        )
        self.refresh_current_page()

    def page_add_member(self):
        self.page_header("Add Library Member")

        form = ttk.Frame(self.content_frame)
        form.pack(anchor="nw", pady=6)
        form.columnconfigure(1, weight=1)

        self.am_fname = ttk.Entry(form, width=36)
        self.am_lname = ttk.Entry(form, width=36)
        self.am_contact = ttk.Entry(form, width=36)

        self.form_row(form, 0, "First name", self.am_fname)
        self.form_row(form, 1, "Last name", self.am_lname)
        self.form_row(form, 2, "Contact number", self.am_contact)
        self.form_hint(form, 3, "Format: 09xxxxxxxxx")

        bar = ttk.Frame(self.content_frame)
        bar.pack(anchor="w", pady=14)
        ttk.Button(bar, text="Add Member", command=self.submit_add_member).pack(
            side="left"
        )
        ttk.Button(bar, text="Clear", command=self.refresh_current_page).pack(
            side="left", padx=8
        )

        self.am_fname.focus_set()

    @staticmethod
    def _validate_member_name(value, label):
        if not value:
            return f"Member's {label} cannot be empty."
        if not all(ch.isalpha() or ch in " .'-" for ch in value):
            return f"Invalid member {label}."
        if libcore.rep_checker(value):
            return f"Member's {label} contains invalid characters."
        return None

    def submit_add_member(self):
        fname = " ".join(self.am_fname.get().split())
        lname = " ".join(self.am_lname.get().split())
        contact = " ".join(self.am_contact.get().split())

        err = self._validate_member_name(
            fname, "first name"
        ) or self._validate_member_name(lname, "last name")
        if err:
            messagebox.showerror("Add Member", err)
            return

        if not contact:
            messagebox.showerror("Add Member", "Contact number cannot be empty.")
            return
        if not contact.isdigit():
            messagebox.showerror(
                "Add Member", "Contact number contains invalid characters."
            )
            return

        contact_num = "".join(ch for ch in contact if ch.isdigit())
        if len(contact_num) != 11 or not contact_num.startswith("09"):
            messagebox.showerror(
                "Add Member",
                "Invalid contact number. Please use a Philippine contact no.",
            )
            return

        active_hit = None
        reviver = None
        for member in libcore.members:
            dupnum = "".join(c for c in member["contact"] if c.isdigit())
            match = dupnum == contact_num
            if member.get("active", True):
                if match:
                    active_hit = member
                    break
            else:
                if match and not reviver:
                    reviver = member

        if active_hit:
            messagebox.showerror(
                "Add Member",
                "A member with this contact number already exists.\n\n"
                f"MemberID: {active_hit['MemberID']}\n"
                f"Name: {active_hit['first_name'].upper()} "
                f"{active_hit['last_name'].upper()}\n"
                f"Contact: {active_hit['contact']}\n\n"
                "Member was not added.",
            )
            return

        if reviver:
            info = (
                f"A deactivated member matches this contact number.\n\n"
                f"MemberID: {reviver['MemberID']}\n"
                f"Name: {reviver['first_name'].upper()} "
                f"{reviver['last_name'].upper()}\n"
                f"Contact: {reviver['contact']}\n"
            )
            if reviver.get("deactivated"):
                info += (
                    f"Deactivated on: "
                    f"{libcore.format_date(reviver['deactivated'])}\n"
                )
            info += "\nReactivate this member instead of adding a new one?"

            if messagebox.askyesno("Reactivate Member", info):
                reviver["active"] = True
                reviver.pop("deactivated", None)
                libcore.save_db()
                messagebox.showinfo(
                    "Add Member",
                    f"Member {reviver['MemberID']} has been reactivated "
                    f"successfully.",
                )
            else:
                messagebox.showinfo("Add Member", "Member was not added.")
            self.refresh_current_page()
            return

        member_id = libcore.get_MID()
        libcore.members.append(
            {
                "MemberID": member_id,
                "first_name": fname,
                "last_name": lname,
                "contact": contact,
                "active": True,
            }
        )
        libcore.save_db()

        messagebox.showinfo(
            "Add Member",
            f"Member added successfully.\n\nMemberID: {member_id}\n"
            f"Name: {fname.upper()} {lname.upper()}\nContact: {contact}",
        )
        self.refresh_current_page()

    def page_borrow(self):
        self.page_header("Borrow Book")

        pane = ttk.Panedwindow(self.content_frame, orient="horizontal")
        pane.pack(fill="both", expand=True)

        left = ttk.Labelframe(pane, text="Available Books", padding=8)
        right = ttk.Labelframe(pane, text="Active Members", padding=8)
        pane.add(left, weight=3)
        pane.add(right, weight=2)

        cols = ("BookID", "Title", "Author", "Copies")
        holder, self.borrow_book_tree = self.build_tree(
            left,
            cols,
            {"BookID": 80, "Title": 220, "Author": 160, "Copies": 70},
            height=14,
        )
        holder.pack(fill="both", expand=True)

        for b in sorted(
            [x for x in libcore.on_books if x["copy"] > 0], key=lambda x: x["BookID"]
        ):
            self.borrow_book_tree.insert(
                "", "end", values=(b["BookID"], b["title"], b["author"], b["copy"])
            )

        cols2 = ("MemberID", "Name", "Contact")
        holder2, self.borrow_member_tree = self.build_tree(
            right, cols2, {"MemberID": 90, "Name": 170, "Contact": 120}, height=14
        )
        holder2.pack(fill="both", expand=True)

        for m in sorted(
            [x for x in libcore.members if x.get("active", True)],
            key=lambda x: x["MemberID"],
        ):
            self.borrow_member_tree.insert(
                "",
                "end",
                values=(
                    m["MemberID"],
                    f"{m['first_name']} {m['last_name']}",
                    m["contact"],
                ),
            )

        entry_bar = ttk.Frame(self.content_frame)
        entry_bar.pack(fill="x", pady=(12, 0))

        ttk.Label(entry_bar, text="BookID:").pack(side="left")
        self.borrow_book_id_var = tk.StringVar()
        self.borrow_book_id_entry = ttk.Entry(
            entry_bar, textvariable=self.borrow_book_id_var, width=14
        )
        self.borrow_book_id_entry.pack(side="left", padx=(6, 20))

        ttk.Label(entry_bar, text="MemberID:").pack(side="left")
        self.borrow_member_id_var = tk.StringVar()
        self.borrow_member_id_entry = ttk.Entry(
            entry_bar, textvariable=self.borrow_member_id_var, width=14
        )
        self.borrow_member_id_entry.pack(side="left", padx=(6, 0))

        self.borrow_book_tree.bind("<<TreeviewSelect>>", self._sync_borrow_book_id)
        self.borrow_member_tree.bind("<<TreeviewSelect>>", self._sync_borrow_member_id)

        self.borrow_book_id_entry.bind("<Return>", lambda e: self._select_borrow_book())
        self.borrow_member_id_entry.bind(
            "<Return>", lambda e: self._select_borrow_member()
        )

        bar = ttk.Frame(self.content_frame)
        bar.pack(fill="x", pady=(10, 0))
        ttk.Button(bar, text="Borrow Selected Book", command=self.do_borrow).pack(
            side="right"
        )

    def _sync_borrow_book_id(self, _event=None):
        sel = self.borrow_book_tree.selection()
        if sel:
            self.borrow_book_id_var.set(self.borrow_book_tree.item(sel[0], "values")[0])

    def _sync_borrow_member_id(self, _event=None):
        sel = self.borrow_member_tree.selection()
        if sel:
            self.borrow_member_id_var.set(
                self.borrow_member_tree.item(sel[0], "values")[0]
            )

    def _select_borrow_book(self):
        target = self.borrow_book_id_var.get().strip().upper()
        if not target:
            return
        for iid in self.borrow_book_tree.get_children():
            if self.borrow_book_tree.item(iid, "values")[0].upper() == target:
                self.borrow_book_tree.selection_set(iid)
                self.borrow_book_tree.see(iid)
                return
        self.borrow_book_tree.selection_remove(*self.borrow_book_tree.selection())

    def _select_borrow_member(self):
        target = self.borrow_member_id_var.get().strip().upper()
        if not target:
            return
        for iid in self.borrow_member_tree.get_children():
            if self.borrow_member_tree.item(iid, "values")[0].upper() == target:
                self.borrow_member_tree.selection_set(iid)
                self.borrow_member_tree.see(iid)
                return
        self.borrow_member_tree.selection_remove(*self.borrow_member_tree.selection())

    def do_borrow(self):
        self._select_borrow_book()
        self._select_borrow_member()

        book_id = self.borrow_book_id_var.get().strip().upper()
        member_id = self.borrow_member_id_var.get().strip().upper()

        if not book_id:
            messagebox.showwarning("Borrow", "Enter or select a BookID.")
            return
        if not member_id:
            messagebox.showwarning("Borrow", "Enter or select a MemberID.")
            return

        book = libcore.find_book(book_id)
        member = libcore.find_member(member_id)

        if not book or book["copy"] <= 0:
            messagebox.showerror(
                "Borrow", f"BookID '{book_id}' not found or has no copies available."
            )
            self.refresh_current_page()
            return
        if not member:
            messagebox.showerror(
                "Borrow", f"MemberID '{member_id}' not found or is inactive."
            )
            self.refresh_current_page()
            return

        book_check = [
            r for r in libcore.off_books if r["MemberID"] == member["MemberID"]
        ]

        overdue = [r for r in book_check if libcore.now() > libcore.to_date(r["due"])]
        if overdue:
            lines = []
            for r in overdue:
                due = libcore.to_date(r["due"])
                late = (libcore.now().date() - due.date()).days
                fine = (
                    libcore.settings["initial_fine"]
                    + late * libcore.settings["missed_fine"]
                )
                lines.append(
                    f"- {r['BookID']}: {r['title']} | Due "
                    f"{due.strftime('%Y-%m-%d')} | {late} day(s) "
                    f"| PHP {fine}"
                )
            messagebox.showerror(
                "Borrow",
                f"{member['first_name']} {member['last_name']} has "
                f"{len(overdue)} overdue book(s).\n"
                "Overdue books must be returned before borrowing again.\n\n"
                + "\n".join(lines),
            )
            return

        unpaid = [
            r
            for r in libcore.dead_books
            if r.get("MemberID") == member["MemberID"] and not r.get("paid", False)
        ]
        if unpaid:
            lines = [
                f"- {r['BookID']}: {r.get('title', 'Unknown')} | "
                f"{r.get('status', 'Unknown')} | "
                f"PHP {r.get('fee', libcore.settings['compensation_fee'])}"
                for r in unpaid
            ]
            messagebox.showerror(
                "Borrow",
                f"{member['first_name']} {member['last_name']} has "
                f"{len(unpaid)} unpaid lost/damaged book(s).\n"
                "These must be compensated before borrowing again.\n\n"
                + "\n".join(lines),
            )
            return

        if len(book_check) >= libcore.settings["max_borrow"]:
            lines = [
                f"- {r['BookID']}: {r['title']} "
                f"(Due {libcore.to_date(r['due']).strftime('%Y-%m-%d')})"
                for r in book_check
            ]
            messagebox.showerror(
                "Borrow",
                f"{member['first_name']} {member['last_name']} already has "
                f"{len(book_check)} borrowed book(s).\n"
                f"Members may only borrow up to "
                f"{libcore.settings['max_borrow']} books at a time.\n\n"
                + "\n".join(lines),
            )
            return

        for r in book_check:
            if r["BookID"].upper() == book["BookID"].upper():
                messagebox.showerror(
                    "Borrow",
                    f"{member['first_name']} {member['last_name']} already "
                    f"borrowed this book.\n\nBookID: {r['BookID']}\n"
                    f"Title: {r['title']}\n"
                    f"Due: {libcore.to_date(r['due']).strftime('%Y-%m-%d')}",
                )
                return

        borrower_name = f"{member['first_name']} {member['last_name']}"
        borrower_contact = member.get("contact")

        if not messagebox.askyesno(
            "Borrow",
            f"Confirm borrowing?\n\nBook: {book['title']} "
            f"({book['BookID']})\nMember: {borrower_name} "
            f"({member['MemberID']})",
        ):
            return

        book["copy"] -= 1
        borrowed_date = libcore.now()
        due_date = borrowed_date + timedelta(days=libcore.settings["due_days"])

        libcore.off_books.append(
            {
                "BookID": book["BookID"],
                "title": book["title"],
                "author": book["author"],
                "MemberID": member["MemberID"],
                "genre": book.get("genre", "Unspecified"),
                "borrower": borrower_name,
                "contact": borrower_contact,
                "borrowed": libcore.to_string(borrowed_date),
                "due": libcore.to_string(due_date),
            }
        )
        libcore.save_db()

        messagebox.showinfo(
            "Borrow",
            f"Book borrowed successfully.\n\nBookID: {book['BookID']}\n"
            f"MemberID: {member['MemberID']}\nBorrower: {borrower_name}\n"
            f"Contact: {borrower_contact}\n"
            f"Due Date: {due_date.strftime('%Y-%m-%d')}\n"
            f"Remaining copies: {book['copy']}",
        )
        self.refresh_current_page()

    def page_return(self):
        self.page_header("Return Book")

        if not libcore.off_books:
            ttk.Label(self.content_frame, text="No borrowed books.").pack(pady=20)
            return

        cols = ("BookID", "Title", "MemberID", "Borrower", "Due", "Status")
        holder, self.return_tree = self.build_tree(
            self.content_frame,
            cols,
            {
                "BookID": 80,
                "Title": 240,
                "MemberID": 90,
                "Borrower": 180,
                "Due": 130,
                "Status": 160,
            },
            height=16,
        )
        holder.pack(fill="both", expand=True)

        current = libcore.now()
        for r in sorted(libcore.off_books, key=lambda x: x["BookID"]):
            due = libcore.to_date(r["due"])
            status = (
                f"Overdue by {(current.date() - due.date()).days} day(s)"
                if current > due
                else "On time"
            )
            self.return_tree.insert(
                "",
                "end",
                values=(
                    r["BookID"],
                    r["title"],
                    r["MemberID"],
                    r.get("borrower", ""),
                    due.strftime("%Y-%m-%d"),
                    status,
                ),
            )

        form = ttk.Frame(self.content_frame)
        form.pack(fill="x", pady=12)

        ttk.Label(form, text="Condition:").pack(side="left")
        self.condition_var = tk.StringVar(value="good")
        ttk.Combobox(
            form,
            textvariable=self.condition_var,
            width=12,
            state="readonly",
            values=("good", "damaged", "lost"),
        ).pack(side="left", padx=8)

        self.paid_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            form, text="Compensated (for damaged/lost)", variable=self.paid_var
        ).pack(side="left", padx=12)

        ttk.Button(form, text="Return Selected Book", command=self.do_return).pack(
            side="right"
        )

    def do_return(self):
        sel = self.return_tree.selection()
        if not sel:
            messagebox.showwarning("Return", "Select a borrowed book to return.")
            return

        values = self.return_tree.item(sel[0], "values")
        book_id, member_id = values[0], values[2]

        record = libcore.find_off(book_id, member_id)
        if not record:
            messagebox.showerror("Return", "Borrow record no longer exists.")
            self.refresh_current_page()
            return

        condition = self.condition_var.get().strip().lower()
        if condition not in ("good", "damaged", "lost"):
            messagebox.showerror("Return", "Select a valid condition.")
            return

        if condition in ("lost", "damaged"):
            fee = libcore.settings["compensation_fee"]
            paid = self.paid_var.get()

            if not messagebox.askyesno(
                "Return",
                f"Mark {record['BookID']} as {condition.upper()}?\n\n"
                f"Title: {record['title']}\n"
                f"Compensation fee: PHP {fee}\n"
                f"Compensated: {'Yes' if paid else 'No'}",
            ):
                return

            libcore.off_books.remove(record)
            libcore.dead_books.append(
                {
                    "BookID": record["BookID"],
                    "title": record["title"],
                    "author": record["author"],
                    "genre": record.get("genre", "Unspecified"),
                    "MemberID": record["MemberID"],
                    "borrower": record.get("borrower"),
                    "contact": record.get("contact"),
                    "due": record["due"],
                    "status": condition.capitalize(),
                    "fee": fee,
                    "paid": paid,
                    "logged": libcore.to_string(libcore.now()),
                }
            )
            libcore.save_db()

            messagebox.showinfo(
                "Return",
                f"{record['BookID']} marked as {condition}.\n"
                f"Payment status: {'PAID' if paid else 'NOT PAID'}",
            )
            self.refresh_current_page()
            return

        if not messagebox.askyesno(
            "Return",
            f"Return {record['BookID']} - {record['title']} in GOOD " f"condition?",
        ):
            return

        libcore.off_books.remove(record)
        return_date = libcore.now()

        libcore.returned_books.append(
            {
                "BookID": record["BookID"],
                "title": record["title"],
                "author": record["author"],
                "genre": record.get("genre", "Unspecified"),
                "MemberID": record["MemberID"],
                "borrower": record.get("borrower"),
                "contact": record.get("contact"),
                "borrowed": record["borrowed"],
                "due": record["due"],
                "returned": libcore.to_string(return_date),
            }
        )

        existing_book = libcore.find_book(record["BookID"])
        warning = ""
        if existing_book:
            if existing_book["copy"] < libcore.settings["max_copy"]:
                existing_book["copy"] += 1
            else:
                warning = (
                    "\nWarning: Maximum inventory reached. "
                    "Returned copy was not added."
                )
        else:
            libcore.on_books.append(
                {
                    "BookID": record["BookID"],
                    "title": record["title"],
                    "author": record["author"],
                    "genre": record.get("genre", "Unspecified"),
                    "copy": 1,
                }
            )

        libcore.save_db()

        due_date = libcore.to_date(record["due"])
        msg = (
            f"Book returned successfully.\n\nBookID: {record['BookID']}\n"
            f"Title: {record['title']}\nCondition: Good\n"
        )

        if return_date > due_date:
            days = (return_date.date() - due_date.date()).days
            initial = libcore.settings["initial_fine"]
            missed = libcore.settings["missed_fine"]
            total = initial + days * missed
            msg += (
                f"\nOverdue by {days} day(s)\n"
                f"Late fine: PHP {total} "
                f"(PHP {initial} + PHP {missed} x {days})"
            )
        else:
            msg += "\nNo late fine."

        if warning:
            msg += warning

        messagebox.showinfo("Return", msg)
        self.refresh_current_page()

    def page_remove_book(self):
        self.page_header("Remove Book")

        available = [b for b in libcore.on_books if b["copy"] > 0]
        if not available:
            ttk.Label(self.content_frame, text="No books to remove.").pack(pady=20)
            return

        cols = ("BookID", "Title", "Author", "On Shelf")
        holder, self.remove_tree = self.build_tree(
            self.content_frame,
            cols,
            {"BookID": 90, "Title": 340, "Author": 240, "On Shelf": 100},
            height=16,
        )
        holder.pack(fill="both", expand=True)

        for b in sorted(available, key=lambda x: x["BookID"]):
            self.remove_tree.insert(
                "", "end", values=(b["BookID"], b["title"], b["author"], b["copy"])
            )

        form = ttk.Frame(self.content_frame)
        form.pack(fill="x", pady=12)
        ttk.Label(form, text="Copies to remove:").pack(side="left")
        self.remove_copies = ttk.Entry(form, width=10)
        self.remove_copies.pack(side="left", padx=8)
        ttk.Button(form, text="Remove Copies", command=self.do_remove_book).pack(
            side="right"
        )

    # kupal amp
    def do_remove_book(self):
        sel = self.remove_tree.selection()
        if not sel:
            messagebox.showwarning("Remove Book", "Select a book first.")
            return

        book_id = self.remove_tree.item(sel[0], "values")[0]
        book = libcore.find_book(book_id)
        if not book:
            messagebox.showerror("Remove Book", "Book not found.")
            return

        try:
            copies = int(self.remove_copies.get().strip())
        except ValueError:
            messagebox.showerror("Remove Book", "Invalid input.")
            return

        if copies <= 0:
            messagebox.showerror("Remove Book", "Amount must be greater than 0.")
            return
        if copies > book["copy"]:
            messagebox.showerror("Remove Book", "Not enough copies available.")
            return

        if not messagebox.askyesno(
            "Remove Book", f"Remove {copies} copies of BookID {book['BookID']}?"
        ):
            return

        book["copy"] -= copies
        libcore.save_db()

        msg = f"Removed {copies} copies of BookID {book['BookID']}."
        if book["copy"] == 0:
            msg += f"\n{book['BookID']} has no copy left."
        messagebox.showinfo("Remove Book", msg)
        self.refresh_current_page()

    def page_deactivate_member(self):
        self.page_header("Deactivate Member")

        active = [m for m in libcore.members if m.get("active", True)]
        if not active:
            ttk.Label(self.content_frame, text="No registered members.").pack(pady=20)
            return

        cols = ("MemberID", "Name", "Contact", "Borrowing", "Unpaid")
        holder, self.deact_tree = self.build_tree(
            self.content_frame,
            cols,
            {
                "MemberID": 100,
                "Name": 260,
                "Contact": 150,
                "Borrowing": 120,
                "Unpaid": 120,
            },
            height=16,
        )
        holder.pack(fill="both", expand=True)

        for m in sorted(active, key=lambda x: x["MemberID"]):
            borrowed = sum(
                1 for r in libcore.off_books if r["MemberID"] == m["MemberID"]
            )
            unpaid = sum(
                1
                for r in libcore.dead_books
                if r.get("MemberID") == m["MemberID"] and not r.get("paid")
            )
            self.deact_tree.insert(
                "",
                "end",
                values=(
                    m["MemberID"],
                    f"{m['first_name']} {m['last_name']}",
                    m["contact"],
                    f"{borrowed} book(s)",
                    f"{unpaid} item(s)",
                ),
            )

        bar = ttk.Frame(self.content_frame)
        bar.pack(fill="x", pady=12)
        ttk.Button(
            bar, text="Deactivate Selected Member", command=self.do_deactivate_member
        ).pack(side="right")

    def do_deactivate_member(self):
        sel = self.deact_tree.selection()
        if not sel:
            messagebox.showwarning("Deactivate", "Select a member first.")
            return

        member_id = self.deact_tree.item(sel[0], "values")[0]
        member = libcore.find_member(member_id)
        if not member:
            messagebox.showerror("Deactivate", "Member not found.")
            return

        borrowed = [r for r in libcore.off_books if r["MemberID"] == member["MemberID"]]
        unpaid = [
            r
            for r in libcore.dead_books
            if r.get("MemberID") == member["MemberID"] and not r.get("paid", False)
        ]

        if borrowed or unpaid:
            lines = [f"Cannot remove member {member['MemberID']}."]
            if borrowed:
                lines.append(
                    f"\nMember currently has {len(borrowed)} borrowed book(s):"
                )
                for r in borrowed:
                    due = libcore.to_date(r["due"])
                    lines.append(
                        f"  - {r['BookID']}: {r['title']} "
                        f"(Due: {due.strftime('%Y-%m-%d')})"
                    )
            if unpaid:
                lines.append(f"\nMember has {len(unpaid)} unpaid damaged/lost book(s):")
                for r in unpaid:
                    fee = r.get("fee", libcore.settings["compensation_fee"])
                    lines.append(
                        f"  - {r['BookID']}: "
                        f"{r.get('title', 'Unknown')} | Fee: PHP {fee}"
                    )
            lines.append(
                "\nAll borrowed books must be returned and all damaged/lost "
                "books compensated before this member can be removed."
            )
            messagebox.showerror("Deactivate", "\n".join(lines))
            return

        if not messagebox.askyesno(
            "Deactivate",
            f"Deactivate member {member['MemberID']} - "
            f"{member['first_name']} {member['last_name']}?",
        ):
            return

        member["active"] = False
        member["deactivated"] = libcore.to_string(libcore.now())
        libcore.save_db()

        messagebox.showinfo(
            "Deactivate",
            f"Member {member['MemberID']} has been deactivated successfully.",
        )
        self.refresh_current_page()

    def page_settings(self):
        self.page_header(
            "Manage Settings", "Adjust lending rules, fines, and inventory limits."
        )

        form = ttk.Frame(self.content_frame)
        form.pack(anchor="nw", pady=6)
        form.columnconfigure(1, weight=1)

        self.setting_vars = {}
        for i, (key, label, _limit) in enumerate(FIELDS):
            var = tk.StringVar(value=str(libcore.settings[key]))
            entry = ttk.Entry(form, textvariable=var, width=20)
            self.form_row(form, i, label, entry)
            self.setting_vars[key] = var

        bar = ttk.Frame(self.content_frame)
        bar.pack(anchor="w", pady=14)
        ttk.Button(bar, text="Save Settings", command=self.save_settings).pack(
            side="left"
        )
        ttk.Button(bar, text="Reload", command=self.refresh_current_page).pack(
            side="left", padx=8
        )

    def save_settings(self):
        new_values = {}

        for key, label, limit in FIELDS:
            raw = self.setting_vars[key].get().strip()
            try:
                value = int(raw)
            except ValueError:
                messagebox.showerror("Settings", f"{label}: invalid number.")
                return
            if value <= 0:
                messagebox.showerror("Settings", f"{label} must be greater than 0.")
                return
            if limit and value > limit:
                messagebox.showerror("Settings", f"{label} cannot exceed {limit}.")
                return
            new_values[key] = value

        if not messagebox.askyesno("Settings", "Confirm these changes?"):
            return

        for key, value in new_values.items():
            libcore.settings[key] = value
        libcore.save_db()

        messagebox.showinfo("Settings", "Settings updated successfully.")
        self.refresh_current_page()

    def page_users(self):
        self.page_header("Manage Users", refresh=True)

        cols = ("Username", "Role")
        holder, self.user_tree = self.build_tree(
            self.content_frame, cols, {"Username": 260, "Role": 260}, height=10
        )
        holder.pack(fill="both", expand=True)
        self.refresh_users()

        bar = ttk.Frame(self.content_frame)
        bar.pack(fill="x", pady=12)
        ttk.Button(bar, text="Change Username", command=self.change_username).pack(
            side="left", padx=4
        )
        ttk.Button(bar, text="Change Password", command=self.change_password).pack(
            side="left", padx=4
        )
        ttk.Button(bar, text="Reset All Credentials", command=self.reset_users).pack(
            side="left", padx=4
        )

    def refresh_users(self):
        self.user_tree.delete(*self.user_tree.get_children())
        for username, info in libcore.users.items():
            self.user_tree.insert("", "end", values=(username, info["role"]))

    def change_username(self):
        sel = self.user_tree.selection()
        if not sel:
            messagebox.showwarning("Users", "Select a user first.")
            return

        username = self.user_tree.item(sel[0], "values")[0]
        new_username = simpledialog.askstring(
            "Change Username", f"New username for '{username}':", parent=self.root
        )
        if new_username is None:
            return
        new_username = new_username.strip()

        if not new_username:
            messagebox.showerror("Users", "Username cannot be empty.")
            return
        if new_username in libcore.users:
            messagebox.showerror("Users", "Username already exists.")
            return
        if len(new_username) > 10:
            messagebox.showerror("Users", "Invalid username length (max 10).")
            return
        if not new_username.isalnum():
            messagebox.showerror(
                "Users", "Invalid username. Use letters and numbers only."
            )
            return
        if len(set(new_username)) == 1:
            messagebox.showerror("Users", "Invalid username.")
            return

        if not messagebox.askyesno(
            "Users", f"Rename '{username}' to '{new_username}'?"
        ):
            return

        libcore.users[new_username] = libcore.users.pop(username)
        libcore.save_db()
        messagebox.showinfo("Users", "Username updated successfully.")
        self.refresh_users()

    def change_password(self):
        sel = self.user_tree.selection()
        if not sel:
            messagebox.showwarning("Users", "Select a user first.")
            return

        username = self.user_tree.item(sel[0], "values")[0]
        new_password = simpledialog.askstring(
            "Change Password",
            f"New password for '{username}':",
            parent=self.root,
            show="*",
        )
        if new_password is None:
            return
        new_password = new_password.strip()

        if not new_password:
            messagebox.showerror("Users", "Password cannot be empty.")
            return
        if len(new_password) > 10:
            messagebox.showerror(
                "Users", "Password length must be at most 10 characters."
            )
            return
        if any(ch.isspace() for ch in new_password):
            messagebox.showerror("Users", "Password cannot contain spaces.")
            return
        if len(set(new_password)) == 1:
            messagebox.showerror("Users", "Invalid password.")
            return

        if not messagebox.askyesno("Users", f"Change password for '{username}'?"):
            return

        libcore.users[username]["password"] = new_password
        libcore.save_db()
        messagebox.showinfo("Users", "Password updated successfully.")

    def reset_users(self):
        if not messagebox.askyesno(
            "Users",
            "Reset ALL user credentials to default?\n\n"
            "admin / admin123\nlibrarian / lib123",
        ):
            return

        libcore.users.clear()
        libcore.users.update(
            {
                "admin": {"password": "admin123", "role": "Administrator"},
                "librarian": {"password": "lib123", "role": "Librarian"},
            }
        )
        libcore.save_db()
        messagebox.showinfo("Users", "All user credentials have been reset to default.")
        self.refresh_users()


def main():
    root = tk.Tk()
    LibSys(root)
    root.mainloop()


if __name__ == "__main__":
    main()
