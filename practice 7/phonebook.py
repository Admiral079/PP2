import csv
from connect import conn, cur

def insert_from_csv():
    with open("contacts.csv", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()

def insert_from_console():
    name = input()
    phone = input()
    cur.execute("INSERT INTO contacts (name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()

def show_all():
    cur.execute("SELECT * FROM contacts")
    for row in cur.fetchall():
        print(row)

def search():
    text = input()
    cur.execute("SELECT * FROM contacts WHERE name ILIKE %s OR phone LIKE %s", ('%' + text + '%', text + '%'))
    print(cur.fetchall())

def update():
    name = input()
    new_phone = input()
    cur.execute("UPDATE contacts SET phone = %s WHERE name = %s", (new_phone, name))
    conn.commit()

def delete():
    value = input()
    cur.execute("DELETE FROM contacts WHERE name = %s OR phone = %s", (value, value))
    conn.commit()

while True:
    print("1 CSV")
    print("2 Add")
    print("3 Show")
    print("4 Search")
    print("5 Update")
    print("6 Delete")
    print("0 Exit")

    c = input()

    if c == "1":
        insert_from_csv()
    elif c == "2":
        insert_from_console()
    elif c == "3":
        show_all()
    elif c == "4":
        search()
    elif c == "5":
        update()
    elif c == "6":
        delete()
    elif c == "0":
        break

cur.close()
conn.close()