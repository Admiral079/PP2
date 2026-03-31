from connect import conn, cur

def add_or_update():
    name = input()
    phone = input()
    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()

def show_all():
    cur.execute("SELECT * FROM contacts")
    print(cur.fetchall())

def search():
    text = input()
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (text,))
    print(cur.fetchall())

def pagination():
    lim = int(input())
    off = int(input())
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (lim, off))
    print(cur.fetchall())

def delete():
    val = input()
    cur.execute("CALL delete_contact(%s)", (val,))
    conn.commit()

while True:
    print("1 Add/Update")
    print("2 Show")
    print("3 Search")
    print("4 Pagination")
    print("5 Delete")
    print("0 Exit")

    c = input()

    if c == "1":
        add_or_update()
    elif c == "2":
        show_all()
    elif c == "3":
        search()
    elif c == "4":
        pagination()
    elif c == "5":
        delete()
    elif c == "0":
        break

cur.close()
conn.close()