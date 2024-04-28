import pickle
from datetime import datetime, timedelta
from collections import UserDict
from pathlib import Path

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()
    
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be a string containing exactly 10 digits.")
        self.value = value

class Birthday(Field):
    def __init__(self, value):
        try:
            date_format = "%d.%m.%Y"
            datetime_obj = datetime.strptime(value, date_format)
            self.value = datetime_obj
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError("Phone number not found.")

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = self.find_phone(old_phone)
        if old_phone_obj is None:
            raise ValueError("Old phone number not found.")
        try:
            new_phone_obj = Phone(new_phone)
        except ValueError as e:
            raise ValueError(f"Invalid new phone number: {e}")
        self.remove_phone(old_phone)
        self.phones.append(new_phone_obj)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_phone(self, phone_number):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def __str__(self):
        info = f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
        if self.birthday:
            info += f", birthday: {self.birthday}"
        return info

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Invalid command format. Use: [command] [name] [phone]"

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def get_upcoming_birthdays(book):
    today = datetime.today().date()
    upcoming_birthdays = []

    for record in book.data.values():
        if record.birthday:
            birthday = record.birthday.value.date()
            birthday_this_year = birthday.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            days_until_birthday = (birthday_this_year - today).days
            if days_until_birthday <= 7:
                congratulation_date = birthday_this_year
                if congratulation_date.weekday() >= 5:
                    congratulation_date += timedelta(days=(7 - congratulation_date.weekday()))
                upcoming_birthdays.append({"name": record.name.value, "congratulation_date": congratulation_date.strftime("%d.%m.%Y")})

    return upcoming_birthdays

@input_error
def add_contact(args, book):
    if len(args) == 2:
        name, phone = args
        record = book.find(name)
        if record:
            record.add_phone(phone)
            return "Phone added to existing contact."
        else:
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            return "New contact added."

@input_error
def change_contact(args, book):
    if len(args) == 3:
        name, old_phone, new_phone = args
        record = book.find(name)
        if record:
            record.edit_phone(old_phone, new_phone)
            return "Contact updated."
        else:
            return "Contact not found."

@input_error
def show_phone(args, book):
    if len(args) == 1:
        name = args[0]
        record = book.find(name)
        if record:
            return "\n".join([str(p) for p in record.phones])

@input_error
def show_all(book):
    if book:
        return "\n".join([str(record) for record in book.data.values()])
    else:
        return "Address book is empty."

@input_error
def add_birthday(args, book):
    if len(args) == 2:
        name, birthday = args
        record = book.find(name)
        if record:
            record.add_birthday(birthday)
            return "Birthday added."
        else:
            return "Contact not found."

@input_error
def show_birthday(args, book):
    if len(args) == 1:
        name = args[0]
        record = book.find(name)
        if record and record.birthday:
            return str(record.birthday)
        else:
            return "Birthday not found."

@input_error
def birthdays(args, book):
    upcoming_birthdays = get_upcoming_birthdays(book)
    if upcoming_birthdays:
        return "\n".join([f"{b['name']}: {b['congratulation_date']}" for b in upcoming_birthdays])
    else:
        return "No upcoming birthdays in the next week."

def main():
    book = load_data()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip().lower()
        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")
    save_data(book) 
if __name__ == "__main__":
    main()
