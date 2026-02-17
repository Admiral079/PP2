class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

book1 = Book("1984", "Orwell")

book1.title = "Animal Farm"

del book1.author

print(book1.title)