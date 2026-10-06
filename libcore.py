from datetime import datetime, timedelta
import json
import os
import getpass

lib_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.json")

# Default library data structure
library = {
    "books": [],
    "borrowed": [],
    "returned": [],
    "dead": [],
    "settings": {
        "max_copy": 50,
        "due_days": 14,
        "max_title": 50,
        "max_author": 25,
        "initial_fine": 50,
        "max_borrow": 3,
        "missed_fine": 5,
        "compensation_fee": 500,
    },
    "members": [],
    "users": {
        "admin": {"password": "admin123", "role": "Administrator"},
        "librarian": {"password": "lib123", "role": "Librarian"},
    },
}

# Color Constants
RED = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[1;34m"
MAGENTA = "\033[1;35m"
CYAN = "\033[1;36m"
RESET = "\033[0m"


# Load database from JSON file; create default if missing
def load_db():
    if not os.path.exists(lib_path):
        with open(lib_path, "w") as f:
            json.dump(library, f, indent=4)
    with open(lib_path, "r") as f:
        data = json.load(f)
    return data


# Save current database to JSON file
def save_db():
    with open(lib_path, "w") as f:
        json.dump(db, f, indent=4)


db = load_db()
members = db["members"]
on_books = db["books"]
off_books = db["borrowed"]
returned_books = db["returned"]
dead_books = db["dead"]
settings = db["settings"]
users = db["users"]


# Clear terminal screen
def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


# Print a header with centered text
def header(text, width=40):
    print("=" * width)
    print(text.center(width))
    print("=" * width)


# Return current datetime
def now():
    return datetime.now()


# Convert datetime to ISO string
def to_string(date):
    return date.isoformat()


# Convert ISO string to datetime
def to_date(text):
    return datetime.fromisoformat(text)


# Format ISO string to readable date-time
def format_date(text):
    return to_date(text).strftime("%Y-%m-%d %H:%M")


# Yes/No/Exit prompt handler
def yn(prompt):
    while True:
        answer = input(prompt).strip().lower()

        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False
        if answer == "exit":
            return None

        print("Please enter yes, no, or exit.")


# Checker if text is repetitive (e.g., "aaaa") or too short
def rep_checker(text):
    check = "".join(text.split())

    if len(check) <= 2:
        return False

    return len(set(check.lower())) == 1


# Generate next sequential ID with given prefix
def get_id(items, key, prefix):
    highest = 0

    for item in items:
        value = str(item.get(key))
        if value.upper().startswith(prefix):
            number = value[len(prefix) :]
            if number.isdigit():
                highest = max(highest, int(number))

    return f"{prefix}{highest + 1:04d}"


# Generate new BookID
def get_BID():
    active_books = on_books + off_books + returned_books + dead_books
    return get_id(active_books, "BookID", "B")


# Generate new MemberID
def get_MID():
    get_members = members + off_books + returned_books + dead_books
    return get_id(get_members, "MemberID", "M")


# Find a book record by title, author, and genre across all collections
def find_record(title, author, genre):
    title = title.strip().lower()
    author = author.strip().lower()
    genre = genre.strip().lower()
    all_books = on_books + off_books + returned_books + dead_books

    for record in all_books:
        if (
            record.get("title").strip().lower() == title
            and record.get("author").strip().lower() == author
            and record.get("genre").strip().lower() == genre
        ):
            return record
    return None


# Find a book on shelf by BookID
def find_book(book_id):
    book_id = book_id.strip().upper()

    for book in on_books:
        if book["BookID"].upper() == book_id:
            return book
    return None


# Find an active member by MemberID
def find_member(member_id):
    member_id = member_id.strip().upper()

    for member in members:
        if member["MemberID"].upper() == member_id and member.get("active", True):
            return member
    return None


# Find a borrowed record by BookID (and optionally MemberID)
def find_off(book_id, member_id=None):
    book_id = book_id.strip().upper()

    for record in off_books:
        if record["BookID"].upper() == book_id:
            if member_id is None:
                return record
            if record["MemberID"].upper() == member_id.strip().upper():
                return record
    return None


# Find a dead (lost/damaged) record by BookID (and optionally MemberID)
def find_dead(book_id, member_id=None):
    book_id = book_id.strip().upper()

    for record in dead_books:
        if record["BookID"].upper() == book_id:
            if member_id is None:
                return record
            if record["MemberID"].upper() == member_id.strip().upper():
                return record
    return None


# Find a returned record by BookID (and optionally MemberID)
def find_returned(book_id, member_id=None):
    book_id = book_id.strip().upper()

    for record in returned_books:
        if record["BookID"].upper() == book_id:
            if member_id is None:
                return record
            if record["MemberID"].upper() == member_id.strip().upper():
                return record
    return None


# Login with username/password, max 3 attempts
def login():
    clear()
    max_attempts = 3
    retry = 0

    while retry < max_attempts:
        header("Login", width=20)
        username = input("Username: ").strip()

        # checker if username exists
        if username not in users:
            print("Invalid Credentials\n")
            retry += 1
            if retry < max_attempts:
                input(
                    f"Press enter to continue ({max_attempts - retry} attempts remaining)"
                )
                clear()
            continue

        password = getpass.getpass("Password: ").strip()

        # Validate password
        if users[username]["password"] == password:
            input("\nLogin Successful! Press Enter to continue.")
            return users[username]["role"]

        print("Invalid Password\n")
        retry += 1
        if retry < max_attempts:
            input(
                f"Press enter to continue ({max_attempts - retry} attempts remaining)"
            )
            clear()

    print(f"{RED}Too many failed attempts. Exiting Terminal.{RESET}")
    input("Press enter to exit Terminal.")
    exit()


# Search books by title, author, genre, or BookID
def search_books():
    clear()
    header("Search Books", width=20)
    print("\nSearch by: title, author, genre, or BookID")
    print("Type 'exit' to cancel.\n")

    while True:
        query = input("Search: ").strip().lower()

        # Handle exit
        if query.lower() == "exit":
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return
        if not query:
            print("Search query cannot be empty.")
            continue

        results = []

        # Search on-shelf books
        for book in on_books:
            if (
                query in book["title"].lower()
                or query in book["author"].lower()
                or query in book["genre"].lower()
                or query in book["BookID"].lower()
            ):
                if book["copy"] > 0:
                    results.append(("Available", book))
                else:
                    results.append(("Unavailable", book))

        # Search borrowed books
        for record in off_books:
            if (
                query in record["title"].lower()
                or query in record["author"].lower()
                or query in record["genre"].lower()
                or query in record["BookID"].lower()
            ):
                results.append(("Borrowed", record))

        # No results handling
        if not results:
            print(f"\nNo matching books found '{query}'.")

            again = yn("\nSearch again? (yes/no): ")

            if again:
                clear()
                header("Search Books", width=20)
                print("Search by: title, author, genre, or BookID")
                print("Type 'exit' to cancel.\n")
                continue

            print("Returning to menu.")
            input("\nPress enter to continue.")
            clear()
            return

        # Display results
        print(f"\nFound {len(results)} result(s):")
        print("=" * 50)

        for status, book in results:
            print(f"\nStatus: {status}")
            print(f"BookID: {book['BookID']}")
            print(f"Title: {book['title'].upper()}")
            print(f"Author: {book['author'].upper()}")
            print(f"Genre: {book['genre'].upper()}")

            if status == "Available":
                print(f"Available Copies: {book['copy']}")
            elif status == "Unavailable":
                print("Available Copies: 0 (No copies available)")
            elif status == "Borrowed":
                print(f"Borrower: {book['borrower'].upper()}")
                print(f"MemberID: {book['MemberID']}")
                print(f"Due Date: {format_date(book['due'])}")
            print("\n" + "-" * 50)

        print("\n" + "=" * 50)

        # Ask to search again
        again = yn("\nSearch again? (yes/no): ")

        if again:
            clear()
            header("Search Books", width=20)
            print("\nSearch by: title, author, genre, or BookID")
            print("Type 'exit' to cancel.\n")

        if again is None or not again:
            print("Returning to menu.")
            input("\nPress enter to continue.")
            clear()
            return


# Add a new library member
def add_member():
    clear()
    header("Add Library Member", width=20)
    print("Type 'exit' to cancel.\n")

    # Input and validate first name
    while True:
        fname = " ".join(input("Enter new member's first name: ").split())

        if fname.lower() == "exit":
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return
        if not fname:
            print("Member's first name cannot be empty.")
            continue
        if not all(char.isalpha() or char in " .'-" for char in fname):
            print("Invalid member first name.")
            continue
        if rep_checker(fname):
            print("Member's first name contains invalid characters.")
            continue
        break

    # Input and validate last name
    while True:
        lname = " ".join(input("Enter new member's last name: ").split())

        if lname.lower() == "exit":
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return
        if not lname:
            print("Member's last name cannot be empty.")
            continue
        if not all(char.isalpha() or char in " .'-" for char in lname):
            print("Invalid member last name.")
            continue
        if rep_checker(lname):
            print("Member's last name contains invalid characters.")
            continue
        break

    # Input and validate contact number
    while True:
        contact = " ".join(input("Enter contact number: ").split())

        if contact.lower() == "exit":
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return
        if not contact:
            print("Contact number cannot be empty.")
            continue
        if not all(char.isdigit() for char in contact):
            print("Contact number contains invalid characters.")
            continue

        contact_num = "".join(char for char in contact if char.isdigit())

        if len(contact_num) != 11 or not contact_num.startswith("09"):
            print("Invalid contact number. Please use Philippine contact no.")
            continue

        # Duplicate and Deactivated Member Checker.
        active_hit = None
        reviver = None

        for member in members:
            dupnum = "".join(c for c in member["contact"] if c.isdigit())

            contact_match = dupnum == contact_num

            if member.get("active", True):
                if contact_match:
                    active_hit = member
                    break
            else:
                if contact_match and not reviver:
                    reviver = member

        if active_hit:
            print("\nA member with this contact number already exists.\n")
            print(f"MemberID: {active_hit['MemberID']}")
            print(
                f"Name: {active_hit['first_name'].upper()} {active_hit['last_name'].upper()}"
            )
            print(f"Contact: {active_hit['contact']}")
            print("\nMember was not added.")
            input("Press Enter to continue.")
            clear()
            return

        if reviver:
            print("\nA deactivated member matches this name and contact number.\n")
            print(f"MemberID: {reviver['MemberID']}")
            print(
                f"Name: {reviver['first_name'].upper()} {reviver['last_name'].upper()}"
            )
            print(f"Contact: {reviver['contact']}")
            if reviver.get("deactivated"):
                print(f"Deactivated on: {format_date(reviver['deactivated'])}")

            choice = yn(
                "\nReactivate this member instead of adding a new one? (yes/no): "
            )

            if choice is None:
                print("Operation cancelled.")
                input("\nPress enter to continue.")
                clear()
                return
            if not choice:
                print("\nMember was not added.")
                input("\nPress enter to continue.")
                clear()
                return

            reviver["active"] = True
            reviver.pop("deactivated", None)
            save_db()

            print(f"\nMember {reviver['MemberID']} has been reactivated successfully.")
            print(
                f"Name: {reviver['first_name'].upper()} {reviver['last_name'].upper()}"
            )
            print(f"Contact: {reviver['contact']}")
            input("\nPress enter to continue.")
            clear()
            return

        break

    # Create new member record
    member_id = get_MID()
    members.append(
        {
            "MemberID": member_id,
            "first_name": fname,
            "last_name": lname,
            "contact": contact,
            "active": True,
        }
    )
    save_db()

    print("\nMember added successfully.")
    print(f"MemberID: {member_id}")
    print(f"Name: {fname.upper()} {lname.upper()}")
    print(f"Contact: {contact}")
    input("\nPress enter to continue.")
    clear()


# Search members by name, contact, or MemberID
def search_members_menu():
    clear()
    header("Search Members", width=20)
    print("Search by: name, contact, or MemberID")
    print("Type 'exit' to cancel.\n")

    while True:
        query = input("Search: ").strip()

        if query.lower() == "exit":
            print("Returning to menu.")
            input("\nPress enter to continue.")
            clear()
            return

        if not query:
            print("Search query cannot be empty.")
            continue

        query = query.lower()
        results = []

        # Search active members
        for member in members:
            if not member.get("active", True):
                continue

            fullname = f"{member['first_name']} {member['last_name']}".lower()
            if (
                query in fullname
                or query in member["contact"].lower()
                or query in member["MemberID"].lower()
            ):
                results.append(member)

        if not results:
            print(f"\nNo members found matching '{query}'.")

            again = yn("\nSearch again? (yes/no): ")

            if again:
                clear()
                header("Search Members", width=20)
                print("Search by: name, contact, or MemberID")
                print("Type 'exit' to cancel.\n")
                continue

            print("Returning to menu.")
            input("\nPress enter to continue.")
            clear()
            return

        print(f"\nFound {len(results)} result(s):")
        print("=" * 50)

        # Display member details and current borrowings
        for member in results:
            print(f"\nMemberID: {member['MemberID']}")
            print(f"Name: {member['first_name'].upper()} {member['last_name'].upper()}")
            print(f"Contact: {member['contact']}")

            borrowed = [
                record
                for record in off_books
                if record["MemberID"] == member["MemberID"]
            ]
            if borrowed:
                print(f"Currently Borrowing: {len(borrowed)} book(s)")
                for record in borrowed:
                    due = to_date(record["due"])
                    if now() > due:
                        late = (now().date() - due.date()).days
                        print(
                            f"  - {record['BookID']}: {record['title'].upper()} (OVERDUE by {late} day(s))"
                        )
                    else:
                        print(
                            f"  - {record['BookID']}: {record['title'].upper()} (Due: {due.strftime('%Y-%m-%d')})"
                        )
            else:
                print("Currently Borrowing: None")
            print("\n" + "-" * 50)
        print("\n" + "=" * 50)

        again = yn("\nSearch again? (yes/no): ")

        if again:
            clear()
            header("Search Members", width=20)
            print("Search by: name, contact, or MemberID")
            print("Type 'exit' to cancel.\n")

        if again is None or not again:
            print("Returning to menu.")
            input("\nPress enter to continue.")
            clear()
            return


# View all active members with borrowed count
def view_members():
    clear()
    header("Current Members", width=20)

    if not members:
        print("No registered members.")
        input("Press enter to continue.")
        clear()
        return

    active_members = [member for member in members if member.get("active", True)]

    if not active_members:
        print("No registered members.")
        input("Press enter to continue.")
        clear()
        return

    for member in sorted(active_members, key=lambda x: x["MemberID"]):
        fname = member["first_name"]
        lname = member["last_name"]
        contact = member["contact"]
        borrowed_count = 0

        for record in off_books:
            if record["MemberID"] == member["MemberID"]:
                borrowed_count += 1

        print(f"\nMemberID: {member['MemberID']}")
        print(f"Name: {fname.upper()} {lname.upper()}")
        print(f"Contact: {contact}")
        print(f"Books Borrowed: {borrowed_count}")
        print("\n" + "-" * 30)

    input("\nPress enter to continue.")
    clear()


# View deactivated members
def view_deact():
    clear()
    header("Deactivated Members", width=20)

    deactivated = [member for member in members if not member.get("active", True)]

    if not deactivated:
        print("No deactivated members.")
        input("Press enter to continue.")
        clear()
        return

    for member in sorted(deactivated, key=lambda x: x["MemberID"]):
        fname = member.get("first_name")
        lname = member.get("last_name")
        contact = member.get("contact")
        deactivated_date = member.get("deactivated")

        print(f"\nMemberID: {member['MemberID']}")
        print(f"Name: {fname.upper()} {lname.upper()}")
        print(f"Contact: {contact}")
        print(f"Deactivated: {format_date(deactivated_date)}")

    input("\nPress enter to continue.")
    clear()


# Deactivate a member (requires no borrowed or unpaid books)
def remove_member():
    clear()
    header("Deactivate Members", width=20)
    print("Type 'exit' to cancel.\n")

    active_members = [member for member in members if member.get("active", True)]

    if not active_members:
        print("No registered members.")
        input("Press enter to continue.")
        clear()
        return

    print("\nRegistered Members:")
    for member in sorted(active_members, key=lambda record: record["MemberID"]):
        borrowed_count = sum(
            1 for record in off_books if record["MemberID"] == member["MemberID"]
        )
        print(
            f"{member['MemberID']} | {member['first_name']} {member['last_name']} | {member['contact']} | Currently Borrowing: {borrowed_count} book(s)"
        )

    # Ask for MemberID to deactivate
    while True:
        member_id = input("\nEnter MemberID to remove: ").strip()

        if member_id.lower() == "exit":
            print("Returning to menu.")
            input("\nPress enter to continue.")
            clear()
            return

        member = find_member(member_id)

        if not member:
            print(f"{member_id} not found.")
            continue
        break

    # Checker for active borrowings
    borrowed_books = [
        record for record in off_books if record["MemberID"] == member["MemberID"]
    ]

    # Checker for unpaid lost/damaged books
    unpaid_books = [
        record
        for record in dead_books
        if record.get("MemberID") == member["MemberID"]
        and not record.get("paid", False)
    ]

    if borrowed_books or unpaid_books:
        print(f"\nCannot remove member {member['MemberID']}.")

        if borrowed_books:
            print(f"Member currently has {len(borrowed_books)} borrowed book(s):")
            for record in borrowed_books:
                due = to_date(record["due"])
                print(
                    f"  - {record['BookID']}: {record['title']} (Due: {due.strftime('%Y-%m-%d')})"
                )

        if unpaid_books:
            print(f"\nMember has {len(unpaid_books)} unpaid damaged/lost book(s):")
            for record in unpaid_books:
                fee = record.get("fee", settings["compensation_fee"])
                logged = (
                    format_date(record["logged"]) if record.get("logged") else "Unknown"
                )
                print(
                    f"  - {record['BookID']}: {record.get('title', 'Unknown')} | Fee: ₱{fee} | Logged: {logged}"
                )

        print(
            "\nAll borrowed books must be returned and all damaged/lost books compensated before being able to remove this member."
        )
        input("\nPress enter to continue.")
        clear()
        return

    # Confirm deactivation
    confirm = yn("\nAre you sure you want to remove this member? (yes/no): ")

    if confirm is None:
        print("Operation cancelled.")
        input("\nPress enter to continue.")
        clear()
        return
    if not confirm:
        print("Member removal cancelled.")
        input("\nPress enter to continue.")
        clear()
        return

    member["active"] = False
    member["deactivated"] = to_string(now())
    save_db()

    print(f"\nMember {member['MemberID']} has been deactivated successfully.")
    input("\nPress enter to continue.")
    clear()


# Sub-menu for viewing books
def view_navigation():
    clear()
    while True:
        header("Library Navigation", width=30)
        print("1. View Available Books")
        print("2. View Borrowed Books")
        print("3. View Unavailable Books")
        print("4. View Returned Books")
        print("0. Back")

        choice = input("Choose: ").strip()

        if choice == "1":
            view_on()
        elif choice == "2":
            view_off()
        elif choice == "3":
            view_dead()
        elif choice == "4":
            view_returned()
        elif choice == "0":
            input("\nPress enter to continue.")
            clear()
            return
        else:
            print("Invalid choice.")
            input("\nPress enter to continue.")
            clear()


# Add books to inventory
def add():
    clear()
    header("Add Books", width=20)

    # Input and validate book title
    while True:
        title = " ".join(input("Enter book title: ").split())

        if len(title) > settings["max_title"]:
            print(
                f"Book title is too long. Maximum is {settings['max_title']} characters."
            )
            return
        if (title.isdigit() and len(title) >= 5) or not title:
            print("Invalid Input.")
            return
        if not all(char.isalnum() or char in " .!?,;:-'&" for char in title):
            print("Invalid title.")
            return
        if any(char * 3 in title for char in ".!?,;:-'&"):
            print("Invalid title.")
            return
        if rep_checker(title):
            print("Invalid book title.")
            return
        break

    # Input and validate author
    while True:
        author = " ".join(input("Enter author: ").split())

        if len(author) > settings["max_author"]:
            print(
                f"Author name is too long. Maximum is {settings['max_author']} characters."
            )
            return
        if author.isdigit() or not author:
            print("Invalid Author name.")
            return
        if not all(char.isalpha() or char in " .'-09" for char in author):
            print(
                "Invalid author. Only letters, spaces, periods, hyphens, and apostrophes are allowed."
            )
            return
        if any(char * 3 in author for char in ".'-"):
            print("Invalid Author name.")
            return
        if rep_checker(author):
            print("Invalid Author name.")
            return
        break

    # Input and validate genre
    while True:
        genre = " ".join(input("Enter book genre: ").split())

        if len(genre) > 20:
            print("Book genre is too long.")
            continue
        if not genre:
            print("Invalid Input.")
            continue
        if not all(char.isalnum() or char in " -" for char in genre):
            print("Invalid genre.")
            return
        if rep_checker(genre):
            print("Invalid book genre.")
            return
        break

    # Input and validate number of copies
    while True:
        try:
            copies = int(input("How many copies: ").strip())

            if copies <= 0:
                print("Please enter a valid book quantity.")
                return
            if copies > settings["max_copy"]:
                print("Amount exceeds maximum inventory.")
                return
            break

        except ValueError:
            print("Invalid input.")
            continue

    # Checker if book already exists (same title, author, genre)
    existing = find_record(title, author, genre)

    if existing:
        book_id = existing["BookID"]

        available = find_book(book_id)

        if available:
            # Book is on shelf; checker max copy limit
            if available["copy"] + copies > settings["max_copy"]:
                print(
                    f"Cannot add that many copies. Maximum inventory is {settings['max_copy']} copies."
                )
                return

            confirm = yn("Are you sure you want to add these copies? (yes/no): ")

            if confirm is None or not confirm:
                print("\nReturning to menu...")
                input("\nPress enter to continue.")
                clear()
                return

            available["copy"] += copies
        else:
            # Book exists in records but not on shelf; add new on-shelf entry
            confirm = yn("Are you sure you want to add this book? (yes/no): ")

            if confirm is None or not confirm:
                print("\nReturning to menu...")
                input("\nPress enter to continue.")
                clear()
                return

            on_books.append(
                {
                    "BookID": book_id,
                    "title": title,
                    "author": author,
                    "genre": genre,
                    "copy": copies,
                }
            )

        save_db()
        print(f"\nInventory updated for BookID: {book_id}")
        print(f"Added copies: {copies}")
        input("Press Enter to continue.")
        clear()
        return

    tdupe = title.strip().lower()
    adupe = author.strip().lower()
    check_books = on_books + off_books + returned_books + dead_books

    # Checker for duplicate title+author with different genre
    for record in check_books:
        if (
            record.get("title").strip().lower() == tdupe
            and record.get("author").strip().lower() == adupe
            and record.get("genre").strip().lower() != genre.strip().lower()
        ):

            gdupe = record.get("genre", "Not specified")
            print(
                f"\nA book with the same title and author already exists with genre: {gdupe}"
            )
            answer = yn(f"Did you mean {gdupe}? (yes/no): ")

            if answer is None:
                print("\nReturning to menu...")
                input("\nPress enter to continue.")
                clear()
                return
            if answer:
                genre = gdupe

                existing = find_record(title, author, genre)

                if existing:
                    book_id = existing["BookID"]
                    available = find_book(book_id)

                    if available:
                        if available["copy"] + copies > settings["max_copy"]:
                            print(
                                f"Cannot add that many copies. Maximum inventory is {settings['max_copy']} copies."
                            )
                            return

                        confirm = yn(
                            "Are you sure you want to add these copies? (yes/no): "
                        )

                        if confirm is None or not confirm:
                            print("\nReturning to menu...")
                            input("\nPress enter to continue.")
                            clear()
                            return

                        available["copy"] += copies
                        save_db()
                        print(f"\nInventory updated for BookID: {book_id}")
                        print(f"Added copies: {copies}")
                        input("Press Enter to continue.")
                        clear()
                        return
                    else:
                        confirm = yn(
                            "Are you sure you want to add this book? (yes/no): "
                        )

                        if confirm is None or not confirm:
                            print("\nReturning to menu...")
                            input("\nPress enter to continue.")
                            clear()
                            return

                        on_books.append(
                            {
                                "BookID": book_id,
                                "title": title,
                                "author": author,
                                "genre": genre,
                                "copy": copies,
                            }
                        )
                        save_db()
                        print(f"\nInventory updated for BookID: {book_id}")
                        print(f"Added copies: {copies}")
                        return
            break

    # Confirm adding a completely new book
    confirm = yn("Are you sure you want to add this book? (yes/no): ")

    if confirm is None or not confirm:
        print("\nReturning to menu...")
        input("\nPress enter to continue.")
        clear()
        return

    book_id = get_BID()
    on_books.append(
        {
            "BookID": book_id,
            "title": title,
            "author": author,
            "genre": genre,
            "copy": copies,
        }
    )
    save_db()

    print("\nBook added successfully.")
    print(f"BookID: {book_id}")
    print(f"Title: {title}")
    print(f"Author: {author}")
    print(f"Genre: {genre}")
    print(f"Copies: {copies}\n")
    input("Press Enter to continue.")
    clear()
    return


# Borrow a book
def borrow():
    clear()
    header("Borrow Books", width=20)
    print("Type 'exit' to cancel.")

    available_books = [book for book in on_books if book["copy"] > 0]
    if not available_books:
        print("\nNo books available.")
        return

    print("\nAvailable Books:")
    for book in sorted(available_books, key=lambda x: x["BookID"]):
        print(
            f"{book['BookID']} | {book['title']} by {book['author']} | On Shelf: {book['copy']} copy(s)"
        )

    # Select BookID to borrow
    while True:
        book_id = input("Enter BookID to borrow: ").strip()

        if book_id.lower() == "exit":
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return

        book = find_book(book_id)

        if not book:
            print("BookID not found.")
            continue
        if book["copy"] <= 0:
            print("No copies available for this BookID.")
            continue
        break

    # Select MemberID
    while True:
        member_id = input("Enter MemberID: ").strip()

        if member_id.lower() == "exit":
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return

        member = find_member(member_id)

        if not member:
            print("MemberID not found.")
            continue
        break

    book_check = [
        record for record in off_books if record["MemberID"] == member["MemberID"]
    ]

    # Overdue book blocker
    overdue_books = [record for record in book_check if now() > to_date(record["due"])]

    if overdue_books:
        print(
            f"\n{member['first_name']} {member['last_name']} has {len(overdue_books)} overdue book(s)."
        )
        print("Overdue books must be returned before borrowing again.")
        print("\nOverdue book(s):")

        for record in overdue_books:
            due = to_date(record["due"])
            late = (now().date() - due.date()).days
            initial_fine = settings["initial_fine"]
            missed_fine = settings["missed_fine"]
            total_fine = initial_fine + (late * missed_fine)
            print(
                f"  - {record['BookID']}: {record['title']} | Due: {due.strftime('%Y-%m-%d')} | Overdue by {late} day(s) | Fine: ₱{total_fine}"
            )

        input("\nPress enter to continue.")
        clear()
        return

    # Unpaid book blocker
    unpaid_books = [
        record
        for record in dead_books
        if record.get("MemberID") == member["MemberID"]
        and not record.get("paid", False)
    ]

    if unpaid_books:
        print(
            f"\n{member['first_name']} {member['last_name']} has {len(unpaid_books)} unpaid lost/damaged book(s)."
        )
        print("These must be compensated before borrowing again.")
        print("\nUnpaid book(s):")
        for record in unpaid_books:
            fee = record.get("fee", settings["compensation_fee"])
            logged = format_date(record["logged"])
            print(
                f"  - {record['BookID']}: {record.get('title', 'Unknown')} | Status: {record.get('status', 'Unknown')} | Logged: {logged}"
            )
        input("\nPress enter to continue.")
        clear()
        return

    # Max borrow limit checker
    if len(book_check) >= settings["max_borrow"]:
        print(
            f"\n{member['first_name']} {member['last_name']} already has {len(book_check)} borrowed book(s)."
        )
        print("Members may only borrow up to 3 books at a time.")
        print("\nCurrently borrowed:")
        for record in book_check:
            due = to_date(record["due"])
            print(
                f"  - {record['BookID']}: {record['title']} (Due: {due.strftime('%Y-%m-%d')})"
            )
        input("\nPress enter to continue.")
        clear()
        return

    # Prevent borrowing the same book twice
    for record in book_check:
        if record["BookID"].upper() == book["BookID"].upper():
            print(
                f"\n{member['first_name']} {member['last_name']} already borrowed this book."
            )
            print(f"BookID: {record['BookID']}")
            print(f"Title: {record['title']}")
            print(f"Due Date: {to_date(record['due']).strftime('%Y-%m-%d')}")
            print("\nThe same book cannot be borrowed twice by the same member.")
            input("\nPress enter to continue.")
            clear()
            return

    borrower_name = f"{member['first_name']} {member['last_name']}"
    borrower_contact = member.get("contact")

    # Confirm borrowing
    confirm = yn("Are you sure you want to borrow this book? (yes/no): ")

    if confirm is None or not confirm:
        print("\nReturning to menu...")
        input("\nPress enter to continue.")
        clear()
        return

    # Update inventory and create borrow record
    book["copy"] -= 1
    borrowed_date = now()
    due_date = borrowed_date + timedelta(days=settings["due_days"])
    off_books.append(
        {
            "BookID": book["BookID"],
            "title": book["title"],
            "author": book["author"],
            "MemberID": member["MemberID"],
            "genre": book.get("genre", "Unspecified"),
            "borrower": borrower_name,
            "contact": borrower_contact,
            "borrowed": to_string(borrowed_date),
            "due": to_string(due_date),
        }
    )
    save_db()

    print("\nBook borrowed successfully.")
    print(f"BookID: {book['BookID']}")
    print(f"MemberID: {member['MemberID']}")
    print(f"Borrower: {borrower_name}")
    print(f"Contact: {borrower_contact}")
    print(f"Due Date: {due_date.strftime('%Y-%m-%d')}")

    if book["copy"] > 0:
        print(f"Remaining copies: {book['copy']}")
        input("Press Enter to continue.")
        clear()
    else:
        print("No copies remaining.")
        input("Press Enter to continue.")
        clear()
    return


# Return a borrowed book
def return_book():
    clear()
    print("\n", 5 * "=", "Return Books", 5 * "=")
    print("Type 'exit' to cancel.")

    if not off_books:
        print("\nNo borrowed books.")
        return

    print("\nCurrently Borrowed:")

    # Display all borrowed books with due status
    for record in sorted(off_books, key=lambda x: x["BookID"]):
        due = to_date(record["due"])
        overdue = now() > due
        if overdue:
            late = (now().date() - due.date()).days
            status = f"Overdue by {late} day(s)"
        else:
            status = "On Time"

        print(f"\nBookID: {record['BookID']}")
        print(f"Book Title: {record['title']}")
        print(f"MemberID: {record['MemberID']}")
        print(f"Borrower: {record['borrower']}")
        print(f"Due: {due.strftime('%Y-%m-%d')} ({status})")

    # Select MemberID to return
    while True:
        member_id = input("\nEnter MemberID to return: ").strip()

        if member_id.lower() == "exit":
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return

        matching = [
            record
            for record in off_books
            if record["MemberID"].upper() == member_id.upper()
        ]
        if not matching:
            print("MemberID is not currently borrowing any books.")
            continue
        if len(matching) == 1:
            borrowed_record = matching[0]
            break

        print("\nThis member has multiple borrowed books:")

        for number, record in enumerate(matching, start=1):
            due = to_date(record["due"])
            print(
                f"{number}. {record['BookID']} - {record['title']} - Due: {due.strftime('%Y-%m-%d')}"
            )

        # Select which book to return
        while True:
            choice = input("\nEnter the number of the book to return: ").strip()

            if choice.lower() == "exit":
                print("Returning to menu.")
                input("Press Enter to continue.")
                clear()
                return
            if choice.isdigit():
                choice = int(choice)

                if 1 <= choice <= len(matching):
                    borrowed_record = matching[choice - 1]
                    break

            print("Invalid choice. Please select one of the numbers above.")
        break

    # Input book condition
    while True:
        condition = input("Condition (good/damaged/lost): ").strip().lower()

        if condition == "exit":
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return
        if condition in ("good", "damaged", "lost"):
            break

        print("Invalid condition.")

    # Handle damaged/lost books
    if condition in ("lost", "damaged"):
        fee = settings["compensation_fee"]
        print(f"\nCompensation fee for {condition} book: ₱{fee}")

        paid = yn("Is the book compensated? (yes/no): ")

        if paid is None:
            print("Returning to menu.")
            input("Press Enter to continue.")
            clear()
            return

        off_books.remove(borrowed_record)
        dead_books.append(
            {
                "BookID": borrowed_record["BookID"],
                "title": borrowed_record["title"],
                "author": borrowed_record["author"],
                "genre": borrowed_record.get("genre", "Unspecified"),
                "MemberID": borrowed_record["MemberID"],
                "borrower": borrowed_record.get("borrower"),
                "contact": borrowed_record.get("contact"),
                "due": borrowed_record["due"],
                "status": condition.capitalize(),
                "fee": fee,
                "paid": paid,
                "logged": to_string(now()),
            }
        )

        save_db()
        print(f"{borrowed_record['BookID']} marked as {condition}.")
        return

    # Handle good condition return
    off_books.remove(borrowed_record)
    return_date = now()
    returned_books.append(
        {
            "BookID": borrowed_record["BookID"],
            "title": borrowed_record["title"],
            "author": borrowed_record["author"],
            "genre": borrowed_record["genre"],
            "MemberID": borrowed_record["MemberID"],
            "borrower": borrowed_record.get("borrower"),
            "contact": borrowed_record.get("contact"),
            "borrowed": borrowed_record["borrowed"],
            "due": borrowed_record["due"],
            "returned": to_string(return_date),
        }
    )

    # Increase available copies
    existing_book = find_book(borrowed_record["BookID"])

    if existing_book:
        if existing_book["copy"] < settings["max_copy"]:
            existing_book["copy"] += 1
        else:
            print("\nWarning: Maximum inventory reached.")
            print("Returned copy was not added to shelf.")
    else:
        on_books.append(
            {
                "BookID": borrowed_record["BookID"],
                "title": borrowed_record["title"],
                "author": borrowed_record["author"],
                "genre": borrowed_record["genre"],
                "copy": 1,
            }
        )
    save_db()

    print("\nBook returned successfully.")
    print(f"BookID: {borrowed_record['BookID']}")
    print(f"Book Title: {borrowed_record['title']}")
    print("Condition: Good")

    # Calculate overdue fine if applicable
    due_date = to_date(borrowed_record["due"])

    if return_date > due_date:
        overdue_days = (return_date.date() - due_date.date()).days
        initial_fine = db["settings"]["initial_fine"]
        missed_fine = db["settings"]["missed_fine"]
        total_fine = initial_fine + (overdue_days * missed_fine)
        print(f"Overdue by {overdue_days} day(s)")
        print(
            f"Late fine: ₱{total_fine} (₱{initial_fine} + ₱{missed_fine} × {overdue_days} days)"
        )
    else:
        print("No late fine")

    print("Book is now available.")
    input("Press Enter to continue.")
    clear()
    return


# View available books on shelf
def view_on():
    clear()
    header("Available Books", width=20)

    available_books = [book for book in on_books if book["copy"] > 0]
    if not available_books:
        print("No available books in inventory.")
        input("Press enter to continue.")
        clear()
        return

    for book in sorted(available_books, key=lambda x: x["BookID"]):
        print(f"\nBookID: {book['BookID']}")
        print(f"Title: {book['title'].upper()}")
        print(f"Author: {book['author'].upper()}")
        print(f"Genre: {book.get('genre').upper()}")
        print(f"On Shelf: {book['copy']} copy(s)")

    input("Press Enter to continue.")
    clear()


# View borrowed books and allow due date extension
def view_off():
    clear()
    header("Borrowed Books", width=20)

    if not off_books:
        print("No borrowed books.")
        input("Press enter to continue.")
        clear()
        return

    current = now()

    for record in sorted(
        off_books,
        key=lambda record: (to_date(record["due"]) >= current, to_date(record["due"])),
    ):
        borrowed = to_date(record["borrowed"])
        due = to_date(record["due"])

        print(f"\nBookID: {record['BookID']}")
        print(f"Book Title: {record['title'].upper()}")
        print(f"MemberID: {record['MemberID'].upper()}")
        print(f"Borrower: {record['borrower'].upper()}")
        print(f"Contact number: {record['contact']}")
        print("Borrowed:", borrowed.strftime("%Y-%m-%d %H:%M"))

        if current > due:
            late = (current.date() - due.date()).days
            initial_fine = settings["initial_fine"]
            missed_fine = settings["missed_fine"]
            total_fine = initial_fine + (late * missed_fine)
            print(f"Due Date: {due.strftime('%Y-%m-%d')} (OVERDUE by {late} day(s))")
            print(
                f"Late Fine: ₱{total_fine} (₱{initial_fine} + ₱{missed_fine} × {late} days)"
            )
        else:
            remaining = (due.date() - current.date()).days
            print(
                f"Due Date: {due.strftime('%Y-%m-%d')} ({remaining} day(s) remaining)"
            )

    # Due date options menu
    while True:
        print("\n", 5 * "=", "Due Date Options", 5 * "=")
        print("0. Back")
        print("1. Extend Due Date")

        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("Returning to menu.")
            input("\nPress enter to continue.")
            clear()
            return
        if choice == "1":
            break

        print("\nInvalid choice.")

    # Select MemberID to extend
    while True:
        member_id = input("\nEnter MemberID to extend due date (or 'exit'): ").strip()

        if member_id.lower() == "exit":
            clear()
            return

        matches = [
            record
            for record in off_books
            if record["MemberID"].upper() == member_id.upper()
        ]

        if not matches:
            print("MemberID is not currently borrowing any books.")
            continue
        if len(matches) == 1:
            selected = matches[0]
            break

        print("\nThis member has multiple borrowed books:")
        for number, record in enumerate(matches, start=1):
            due = to_date(record["due"])

            print(
                f"{number}. {record['BookID']} - {record['title']} - Due: {due.strftime('%Y-%m-%d')}"
            )

        # Select which book to extend
        while True:
            choice = input("\nEnter the number of the book to extend: ").strip()

            if choice.lower() == "exit":
                return
            if choice.isdigit():
                choice = int(choice)

                if 1 <= choice <= len(matches):
                    selected = matches[choice - 1]
                    break

            print("Invalid choice. Please select one of the numbers above.")
        break

    selected_due = to_date(selected["due"])

    # Block extension if already overdue
    if now() > selected_due:
        late = (now().date() - selected_due.date()).days
        initial_fine = settings["initial_fine"]
        missed_fine = settings["missed_fine"]
        total_fine = initial_fine + (late * missed_fine)

        print(f"\nThis book is OVERDUE by {late} day(s).")
        print(
            f"Ovedue fine: ₱{total_fine} (₱{initial_fine} + ₱{missed_fine} × {late} days)"
        )
        print("Overdue books cannot be extended.")
        input("\nPress enter to continue.")
        clear()
        return

    # Input extension days
    while True:
        try:
            extra = int(input("Extend by how many days? "))

            if extra <= 0:
                print("Enter a number greater than 0.")
                continue
            if extra > 365:
                print("Due date cannot exceed a year.")
                continue

            new_due = selected_due + timedelta(days=extra)
            selected["due"] = to_string(new_due)
            save_db()

            print("\nDue date updated successfully.")
            print("New Due Date:", new_due.strftime("%Y-%m-%d"))
            input("Press Enter to continue.")
            clear()
            return

        except ValueError:
            print("Enter a valid number.")


# View unavailable (lost/damaged) books and update payment
def view_dead():
    clear()
    header("Unavailable Books", width=20)

    if not dead_books:
        print("No unavailable books.")
        input("Press enter to continue.")
        clear()
        return

    for record in sorted(dead_books, key=lambda x: x["BookID"]):
        fee = record.get("fee", settings["compensation_fee"])
        print(f"\nBookID: {record['BookID']}")
        print(f"Title: {record['title'].upper()}")
        print(f"Author: {record['author'].upper()}")
        print(f"MemberID: {record['MemberID']}")
        print(f"Borrower: {record['borrower'].upper()}")
        print(f"Contact number: {record['contact']}")
        print(f"Status: {record['status']}")
        print(f"Fee: ₱{fee}")
        print(f"Payment: {'PAID' if record['paid'] else 'NOT PAID'}")
        print(f"Logged: {format_date(record['logged'])}")

    # Payment options menu
    while True:
        print("\n", 5 * "=", "Payment Options", 5 * "=")
        print("0. Exit")
        print("1. Update Payment Status")

        choice = input("Enter your choice: ").strip()

        if choice == "0":
            print("Returning to menu.")
            input("\nPress enter to continue.")
            clear()
            return
        if choice == "1":
            break

        print("Invalid Choice")

    unpaid_books = [record for record in dead_books if not record["paid"]]

    if not unpaid_books:
        print("\nNo unpaid books available for payment update.")
        input("Press Enter to continue.")
        clear()
        return

    print("\n", 5 * "=", "Unpaid Books", 5 * "=")
    for record in unpaid_books:
        fee = record.get("fee", settings["compensation_fee"])
        print(
            f"BookID: {record['BookID']} | MemberID: {record['MemberID']} | Borrower: {record['borrower']} | Fee: ₱{fee}"
        )

    # Select BookID to update payment
    while True:
        book_id = input("\nEnter BookID to update payment (or 'exit'): ").strip()

        if book_id.lower() == "exit":
            return

        matches = [
            record
            for record in unpaid_books
            if record["BookID"].upper() == book_id.upper()
        ]

        if not matches:
            print("BookID not found.")
            continue
        if len(matches) > 1:
            member_id = input("Enter MemberID: ").strip()

            if member_id.lower() == "exit":
                return

            selected = find_dead(book_id, member_id)

            if not selected:
                print("BookID and MemberID do not match.")
                continue
        else:
            selected = matches[0]
        break

    clear()
    print(f"\nBookID: {selected['BookID']}")
    print(f"MemberID: {selected['MemberID']}")
    print(f"Borrower: {selected.get('borrower') or 'Name not provided'}")
    print(f"Contact number: {selected.get('contact') or 'Not provided'}")
    print(f"Status: {selected['status']}")
    print(f"Fee: ₱{selected.get('fee', settings['compensation_fee'])}")
    print(f"Logged: {format_date(selected['logged'])}")
    print(f"Current Payment: {'Paid' if selected['paid'] else 'Not Paid'}")

    # Update payment status
    while True:
        print("\n", 5 * "=", "Payment Status", 5 * "=")
        print("0. Exit")
        print("1. Paid")

        choice = input("Enter payment status: ").strip()

        if choice == "0":
            return
        if choice == "1":
            selected["paid"] = True
            break
        print("Invalid Choice")

    save_db()
    print("\nPayment status updated to: Paid")
    input("\nPress enter to continue.")
    clear()


# View returned books
def view_returned():
    clear()
    header("Returned Books", width=20)

    if not returned_books:
        print("No returned books.")
        input("Press enter to continue.")
        clear()
        return

    for record in returned_books:
        print(f"\nBookID: {record['BookID']}")
        print(f"MemberID: {record['MemberID']}")
        print(f"Borrower: {record['borrower'].upper()}")
        print(f"Contact number: {record['contact']}")
        print(f"Borrowed: {format_date(record['borrowed'])}")
        print(f"Due Date: {format_date(record['due'])}")
        print(f"Returned: {format_date(record['returned'])}")
    input("\nPress enter to continue.")
    clear()


# Remove copies from inventory
def remove():
    clear()
    header("Remove Books", width=20)

    available_books = [book for book in on_books if book["copy"] > 0]
    if not available_books:
        print("\nNo books to remove.")
        return

    print("\nAvailable Books:")

    for book in sorted(available_books, key=lambda record: record["BookID"]):
        print(
            f"{book['BookID']} | {book['title']} by {book['author']} | On Shelf: {book['copy']} copy(s)"
        )

    print("\nType 'exit' to cancel.")
    # Select BookID to remove
    while True:
        book_id = input("Enter BookID to remove: ").strip()

        if book_id.lower() == "exit":
            print("Returning to menu.")
            return

        book = find_book(book_id)

        if not book:
            print("BookID not found.")
            continue
        break

    # Input number of copies to remove
    while True:
        try:
            copies = int(
                input(f"How many copies of BookID {book['BookID']} to remove? ").strip()
            )

            if copies <= 0:
                print("Amount must be greater than 0.")
                continue
            if copies > book["copy"]:
                print("Not enough copies available.")
                continue

            confirm = yn(
                f"Remove {copies} copies of BookID {book['BookID']}? (yes/no): "
            )

            if confirm is None:
                print("Returning to menu.")
                input("Press Enter to continue.")
                clear()
                return
            if not confirm:
                print("Removal cancelled.")
                return

            book["copy"] -= copies

            print(f"\nRemoved {copies} copies of BookID {book['BookID']}.")

            save_db()

            if book["copy"] == 0:
                print(f"{book['BookID']} has no copy left.")
                input("Press Enter to continue.")
                clear()

            return

        except ValueError:
            print("Invalid Input")


# Manage library settings
def manage_settings():
    clear()
    while True:
        header("Library Settings", width=20)
        print("Manage inventory and due date default")
        print(f"1. Maximum Copies   : {settings['max_copy']}")
        print(f"2. Borrow Days      : {settings['due_days']}")
        print(f"3. Initial Fine     : {settings['initial_fine']}")
        print(f"4. Missed Days Fine : {settings['missed_fine']}")
        print(f"5. Max Borrow       : {settings['max_borrow']}")
        print(f"6. Compensation Fee : {settings['compensation_fee']}")
        print("0. Back")

        choice = input("Choose: ").strip()

        # Update max copies
        if choice == "1":
            while True:
                try:
                    value = int(input("Enter new maximum copies: "))

                    if value <= 0:
                        print("Must be greater than 0.")
                        continue
                    confirm = yn("Confirm changes? (yes/no): ")

                    if confirm is None or not confirm:
                        print("Operation cancelled.")
                        input("\nPress enter to continue.")
                        clear()
                        break

                    settings["max_copy"] = value
                    save_db()
                    print("Maximum copies updated.")
                    input("\nPress enter to continue.")
                    clear()
                    break

                except ValueError:
                    print("Invalid input.\n")
                    continue

        # Update borrow days
        elif choice == "2":
            while True:
                try:
                    value = int(input("Enter new borrowing period (days): "))

                    if value <= 0:
                        print("Must be greater than 0.")
                        continue
                    if value > 365:
                        print("Borrow days cannot exceed a year.")
                        continue
                    confirm = yn("Confirm changes? (yes/no): ")

                    if confirm is None or not confirm:
                        print("Operation cancelled.")
                        input("\nPress enter to continue.")
                        clear()
                        break

                    settings["due_days"] = value
                    save_db()
                    print("Borrowing period updated.")
                    input("\nPress enter to continue.")
                    clear()
                    break

                except ValueError:
                    print("Invalid input. \n")
                    continue

        # Update initial fine
        elif choice == "3":
            while True:
                try:
                    value = int(input("Enter new initial fine: "))

                    if value <= 0:
                        print("Must be greater than 0.")
                        continue
                    confirm = yn("Confirm changes? (yes/no): ")

                    if confirm is None or not confirm:
                        print("Operation cancelled.")
                        input("\nPress enter to continue.")
                        clear()
                        break

                    settings["initial_fine"] = value
                    save_db()
                    print("Initial Fine updated.")
                    input("\nPress enter to continue.")
                    clear()
                    break

                except ValueError:
                    print("Invalid input. \n")
                    continue

        # Update missed days fine
        elif choice == "4":
            while True:
                try:
                    value = int(input("Enter new missed days fine: "))

                    if value <= 0:
                        print("Must be greater than 0.")
                        continue
                    confirm = yn("Confirm changes? (yes/no): ")

                    if confirm is None or not confirm:
                        print("Operation cancelled.")
                        input("\nPress enter to continue.")
                        clear()
                        break

                    settings["missed_fine"] = value
                    save_db()
                    print("Missed days fine updated.")
                    input("\nPress enter to continue.")
                    clear()
                    break

                except ValueError:
                    print("Invalid input. \n")
                    continue

        # Update max borrow
        elif choice == "5":
            while True:
                try:
                    value = int(input("Enter new max borrow: "))

                    if value <= 0:
                        print("Must be greater than 0.")
                        continue
                    confirm = yn("Confirm changes? (yes/no): ")

                    if confirm is None or not confirm:
                        print("Operation cancelled.")
                        input("\nPress enter to continue.")
                        clear()
                        break

                    settings["max_borrow"] = value
                    save_db()
                    print("Missed max borrow updated.")
                    input("\nPress enter to continue.")
                    clear()
                    break

                except ValueError:
                    print("Invalid input. \n")
                    continue

        # Update lost/damaged compensation
        elif choice == "6":
            while True:
                try:
                    value = int(input("Enter new compensation fee: "))

                    if value <= 0:
                        print("Must be greater than 0.")
                        continue
                    confirm = yn("Confirm changes? (yes/no): ")

                    if confirm is None or not confirm:
                        print("Operation cancelled.")
                        input("\nPress enter to continue.")
                        clear()
                        break

                    settings["compensation_fee"] = value
                    save_db()
                    print("Compensation fee updated.")
                    input("\nPress enter to continue.")
                    clear()
                    break

                except ValueError:
                    print("Invalid input. \n")
                    continue
        elif choice == "0":
            input("Press Enter to continue.")
            clear()
            return


# Manage system users
def manage_users():
    clear()
    while True:
        header("Manage Users", width=20)
        print(f"1. View Users")
        print(f"2. Change Username")
        print(f"3. Change Password")
        print(f"4. {RED}Reset User Credentials{RESET}")
        print(f"0. {RED}Back{RESET}")

        choice = input("Choose: ").strip()

        # View users
        if choice == "1":
            print("\nRegistered Users:")

            for username, info in users.items():
                print(f"Username: {username} | Role: {info['role']}")

            input("\nPress enter to continue.")
            clear()

        # Change username
        elif choice == "2":
            username = input("\nEnter username to change: ").strip()

            if username not in users:
                print("User not found.")
                input("\nPress enter to continue.")
                clear()
                continue

            print(f"\nSelected User: {username}")

            new_username = input("New Username: ").strip()

            # Validate new username
            if not new_username:
                print("\nUsername cannot be empty.")
                continue
            if new_username in users:
                print("\nUsername already exists.")
                input("Press Enter to continue")
                clear()
                continue
            if len(new_username) > 10:
                print("\nInvalid username length.")
                continue
            if not new_username.isalnum():
                print("Invalid Username")
                continue
            if len(set(new_username.replace(" "))) == 1:
                print("\nInvalid username.")
                continue

            confirm = yn("Continue changing this username? (yes/no): ")

            if confirm is None or not confirm:
                print("Operation cancelled.")
                input("\nPress enter to continue.")
                clear()
                continue

            users[new_username] = users.pop(username)
            save_db()
            print("Username updated successfully.")
            input("\nPress enter to continue.")
            clear()

        # Change password
        elif choice == "3":
            username = input("Enter username to change password: ").strip()

            if username not in users:
                print("User not found.")
                input("\nPress enter to continue.")
                clear()
                continue

            print(f"\nSelected User: {username}")
            new_password = getpass.getpass("New Password: ").strip()

            # Validate new password
            if not new_password:
                print("\nPassword cannot be empty.")
                continue
            if len(new_password) > 10:
                print("\nPassword length must be at most 10 characters long.")
                continue
            if len(set(new_password.replace(" "))) == 1:
                print("\nInvalid password.")
                continue
            if any(char.isspace() for char in new_password):
                print("\nPassword cannot contain spaces.")
                continue

            confirm = yn("Continue changing this password? (yes/no): ")

            if confirm is None or not confirm:
                print("Operation cancelled.")
                input("\nPress enter to continue.")
                clear()
                continue

            users[username]["password"] = new_password
            save_db()
            print("Password updated successfully.")
            input("\nPress enter to continue.")
            clear()

        # Reset all credentials to default
        elif choice == "4":
            confirm = yn("Reset ALL user credentials to default? (yes/no): ")

            if confirm is None or not confirm:
                print("Reset cancelled.")
                input("\nPress enter to continue.")
                clear()
                continue

            users.clear()
            users.update(
                {
                    "admin": {"password": "admin123", "role": "Administrator"},
                    "librarian": {"password": "lib123", "role": "Librarian"},
                }
            )
            save_db()
            print("All user credentials have been reset to default.")
            input("\nPress enter to continue.")
            clear()

        elif choice == "0":
            input("\nPress enter to continue.")
            clear()
            return
        else:
            print("Invalid choice.")
            input("\nPress enter to continue.")
            clear()


# Role-based main menu
def menu(role):
    clear()
    while True:
        header(f"Book Borrowing System ({role})", width=40)
        if role == "Administrator":
            print(f"1. Manage Users")
            print(f"2. Manage Settings")
            print(f"3. View Books Navigation")
            print(f"4. View Members")
            print(f"5. Search Members")
            print(f"6. View Deactivated Members")
            print(f"7. {RED}Remove Book{RESET}")
            print(f"8. {RED}Deactivate Member{RESET}")
            print(f"0. {RED}Logout{RESET}")
        elif role == "Librarian":
            print(f"1. Add Book")
            print(f"2. Add Member")
            print(f"3. View Members")
            print(f"4. Search Members")
            print(f"5. View Books Navigation")
            print(f"6. Search Books")
            print(f"7. Borrow Book")
            print(f"8. Return Book")
            print(f"0. {RED}Logout{RESET}")

        choice = input("Enter your choice: ").strip()

        # Logout confirmation
        if choice == "0":
            confirm = yn("Are you sure you want to logout? (yes/no): ")

            if confirm is None or not confirm:
                print("\nReturning to menu...")
                input("\nPress enter to continue.")
                clear()
                continue

            print("\nLogging out...")
            input("\nPress enter to continue.")
            clear()
            return

        if role == "Administrator":
            if choice == "1":
                manage_users()
            elif choice == "2":
                manage_settings()
            elif choice == "3":
                view_navigation()
            elif choice == "4":
                view_members()
            elif choice == "5":
                search_members_menu()
            elif choice == "6":
                view_deact()
            elif choice == "7":
                remove()
            elif choice == "8":
                remove_member()
            else:
                print("Invalid choice.")
                input("\nPress enter to continue.")
                clear()

        elif role == "Librarian":
            if choice == "1":
                add()
            elif choice == "2":
                add_member()
            elif choice == "3":
                view_members()
            elif choice == "4":
                search_members_menu()
            elif choice == "5":
                view_navigation()
            elif choice == "6":
                search_books()
            elif choice == "7":
                borrow()
            elif choice == "8":
                return_book()
            else:
                print("Invalid choice.")
                input("\nPress enter to continue.")
                clear()


# Front program loop
def main():
    while True:
        clear()
        header(f"New Archive Zealous Indexers Library", width=40)
        print(f"\n1. Login")
        print(f"0. {RED}Exit\n{RESET}")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            role = login()

            if role:
                menu(role)
        elif choice == "0":
            confirm = yn("Are you sure you want to exit? (yes/no): ")

            if confirm is None or not confirm:
                print("\nExit cancelled.")
                input("Press enter to continue")
                clear()
                continue

            print("\nThank you for using the system!")
            input("Press enter to exit terminal")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()