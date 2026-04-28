import csv
import json
from pathlib import Path

from connect import get_connection


BASE_DIR = Path(__file__).resolve().parent
SCHEMA_FILE = BASE_DIR / "schema.sql"
PROCEDURES_FILE = BASE_DIR / "procedures.sql"
SORT_FIELDS = {
    "name": "c.name",
    "birthday": "c.birthday NULLS LAST, c.name",
    "date": "c.created_at DESC, c.name",
}


def clean_name(name):
    text = "".join(ch for ch in str(name).strip() if ch.isalnum() or ch in " _-")[:12].strip()
    return text or "Player"


def parse_phones(raw_value):
    if isinstance(raw_value, list):
        phones = []
        for item in raw_value:
            if not isinstance(item, dict):
                continue
            phone_type = str(item.get("type", "mobile")).strip().lower()
            phone = str(item.get("phone", "")).strip()
            if phone and phone_type in {"home", "work", "mobile"}:
                phones.append({"type": phone_type, "phone": phone})
        return phones

    phones = []
    for chunk in str(raw_value or "").split(";"):
        piece = chunk.strip()
        if not piece:
            continue
        if ":" in piece:
            phone_type, phone = piece.split(":", 1)
        else:
            phone_type, phone = "mobile", piece
        phone_type = phone_type.strip().lower()
        phone = phone.strip()
        if phone and phone_type in {"home", "work", "mobile"}:
            phones.append({"type": phone_type, "phone": phone})
    return phones


def load_sql_file(path):
    return path.read_text(encoding="utf-8")


def run_sql_file(conn, path):
    with conn.cursor() as cur:
        cur.execute(load_sql_file(path))
    conn.commit()


def ensure_group(conn, group_name):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO groups (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            """,
            (group_name,),
        )
        cur.execute("SELECT id FROM groups WHERE name = %s", (group_name,))
        return cur.fetchone()["id"]


def contact_exists(conn, name):
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
        row = cur.fetchone()
        return row["id"] if row else None


def save_contact(conn, contact, overwrite=False):
    name = clean_name(contact["name"])
    email = (contact.get("email") or "").strip() or None
    birthday = (contact.get("birthday") or "").strip() or None
    group_name = (contact.get("group") or "Other").strip() or "Other"
    phones = parse_phones(contact.get("phones", ""))
    group_id = ensure_group(conn, group_name)
    contact_id = contact_exists(conn, name)

    with conn.cursor() as cur:
        if contact_id and not overwrite:
            return False
        if contact_id:
            cur.execute(
                """
                UPDATE contacts
                SET email = %s, birthday = %s, group_id = %s
                WHERE id = %s
                """,
                (email, birthday, group_id, contact_id),
            )
            cur.execute("DELETE FROM phones WHERE contact_id = %s", (contact_id,))
        else:
            cur.execute(
                """
                INSERT INTO contacts (name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (name, email, birthday, group_id),
            )
            contact_id = cur.fetchone()["id"]

        for phone in phones:
            cur.execute(
                """
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
                ON CONFLICT (contact_id, phone) DO UPDATE
                SET type = EXCLUDED.type
                """,
                (contact_id, phone["phone"], phone["type"]),
            )

    conn.commit()
    return True


def fetch_contacts(conn, where="", params=(), sort_key="name", limit=None, offset=0):
    order_by = SORT_FIELDS.get(sort_key, SORT_FIELDS["name"])
    query = f"""
        SELECT
            c.name,
            c.email,
            c.birthday,
            COALESCE(g.name, 'Other') AS group_name,
            c.created_at,
            COALESCE(STRING_AGG(p.phone || ' [' || p.type || ']', ', ' ORDER BY p.id), '') AS phones
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        {where}
        GROUP BY c.id, g.name
        ORDER BY {order_by}
    """
    if limit is not None:
        query += " LIMIT %s OFFSET %s"
        params = tuple(params) + (limit, offset)
    with conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall()


def export_contacts(conn):
    rows = fetch_contacts(conn)
    data = []
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                "SELECT phone, type FROM phones WHERE contact_id = (SELECT id FROM contacts WHERE name = %s) ORDER BY id",
                (row["name"],),
            )
            phones = [{"phone": item["phone"], "type": item["type"]} for item in cur.fetchall()]
            data.append(
                {
                    "name": row["name"],
                    "email": row["email"],
                    "birthday": row["birthday"].isoformat() if row["birthday"] else None,
                    "group": row["group_name"],
                    "phones": phones,
                }
            )
    return data


def print_contacts(rows):
    if not rows:
        print("No contacts found.")
        return
    for row in rows:
        birthday = row["birthday"].isoformat() if row["birthday"] else "-"
        print(
            f"{row['name']} | email: {row['email'] or '-'} | birthday: {birthday} | "
            f"group: {row['group_name']} | phones: {row['phones'] or '-'}"
        )


def export_json(conn):
    path = Path(input("JSON file path [contacts.json]: ").strip() or "contacts.json")
    data = export_contacts(conn)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Exported {len(data)} contacts to {path}")


def import_json(conn):
    path = Path(input("JSON file path [contacts.json]: ").strip() or "contacts.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    for item in data:
        name = clean_name(item.get("name", "Player"))
        if contact_exists(conn, name):
            action = input(f'"{name}" already exists. skip or overwrite? ').strip().lower()
            if action == "skip":
                continue
            if action != "overwrite":
                print("Skipped.")
                continue
            overwrite = True
        else:
            overwrite = False
        save_contact(
            conn,
            {
                "name": name,
                "email": item.get("email"),
                "birthday": item.get("birthday"),
                "group": item.get("group"),
                "phones": item.get("phones", []),
            },
            overwrite=overwrite,
        )
    print("JSON import finished.")


def import_csv(conn):
    path = Path(input("CSV file path [contacts.csv]: ").strip() or "contacts.csv")
    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            save_contact(
                conn,
                {
                    "name": row.get("name", ""),
                    "email": row.get("email"),
                    "birthday": row.get("birthday"),
                    "group": row.get("group"),
                    "phones": row.get("phones") or f"{row.get('phone_type', 'mobile')}:{row.get('phone', '')}",
                },
                overwrite=True,
            )
    print("CSV import finished.")


def add_contact_console(conn):
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    birthday = input("Birthday YYYY-MM-DD: ").strip()
    group_name = input("Group [Other]: ").strip() or "Other"
    phones = input("Phones (example: mobile:8701;home:7701): ").strip()
    save_contact(
        conn,
        {"name": name, "email": email, "birthday": birthday, "group": group_name, "phones": phones},
        overwrite=True,
    )
    print("Contact saved.")


def add_phone_console(conn):
    with conn.cursor() as cur:
        cur.execute("CALL add_phone(%s, %s, %s)", (input("Contact name: ").strip(), input("Phone: ").strip(), input("Type home/work/mobile: ").strip().lower()))
    conn.commit()
    print("Phone added.")


def move_group_console(conn):
    with conn.cursor() as cur:
        cur.execute("CALL move_to_group(%s, %s)", (input("Contact name: ").strip(), input("New group: ").strip()))
    conn.commit()
    print("Group updated.")


def search_all_console(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (input("Search text: ").strip(),))
        print_contacts(cur.fetchall())


def search_email_console(conn):
    rows = fetch_contacts(conn, "WHERE COALESCE(c.email, '') ILIKE %s", (f"%{input('Email text: ').strip()}%",))
    print_contacts(rows)


def filter_group_console(conn):
    rows = fetch_contacts(conn, "WHERE COALESCE(g.name, 'Other') = %s", (input("Group name: ").strip(),))
    print_contacts(rows)


def browse_pages_console(conn):
    sort_key = input("Sort by name / birthday / date: ").strip().lower() or "name"
    limit = int(input("Page size [5]: ").strip() or "5")
    offset = 0
    while True:
        rows = fetch_contacts(conn, sort_key=sort_key, limit=limit, offset=offset)
        print(f"\nPage offset={offset}\n")
        print_contacts(rows)
        action = input("\nnext / prev / quit: ").strip().lower()
        if action == "next":
            offset += limit
        elif action == "prev":
            offset = max(0, offset - limit)
        else:
            break


def print_menu():
    print(
        """
1. Add or overwrite contact
2. Add extra phone to contact
3. Move contact to group
4. Search contacts (name/email/group/phones)
5. Search by email
6. Filter by group
7. Browse pages
8. Import CSV
9. Import JSON
10. Export JSON
11. Quit
"""
    )


def main():
    with get_connection() as conn:
        run_sql_file(conn, SCHEMA_FILE)
        run_sql_file(conn, PROCEDURES_FILE)
        actions = {
            "1": lambda: add_contact_console(conn),
            "2": lambda: add_phone_console(conn),
            "3": lambda: move_group_console(conn),
            "4": lambda: search_all_console(conn),
            "5": lambda: search_email_console(conn),
            "6": lambda: filter_group_console(conn),
            "7": lambda: browse_pages_console(conn),
            "8": lambda: import_csv(conn),
            "9": lambda: import_json(conn),
            "10": lambda: export_json(conn),
        }
        while True:
            print_menu()
            choice = input("Choose: ").strip()
            if choice == "11":
                break
            action = actions.get(choice)
            if not action:
                print("Unknown command.")
                continue
            try:
                action()
            except Exception as error:
                conn.rollback()
                print(f"Error: {error}")


if __name__ == "__main__":
    main()