from collections import UserDict
from datetime import datetime, date, timedelta
import pickle  # Додано імпорт pickle

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Контакт не знайдено."
        except IndexError:
            return "Введіть команду та необхідні аргументи."
        except Exception as e:
            return f"Виникла непередбачена помилка: {e}"
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not self.is_valid(value):
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(value)

    def is_valid(self, value):
        return value.isdigit() and len(value) == 10

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        try:
            phone_obj = Phone(phone)
            if phone_obj not in self.phones:
                self.phones.append(phone_obj)
        except ValueError as e:
            print(e)

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        found = False
        for phone in self.phones:
            if phone.value == old_phone:
                try:
                    phone.value = new_phone
                    found = True
                    break
                except ValueError as e:
                    print(e)
                return
        if not found:
            print(f"Phone number {old_phone} not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        try:
            self.birthday = Birthday(birthday)
            print("Birthday added.")
        except ValueError as e:
            print(e)

    def __str__(self):
        birthday_str = f", birthday: {self.birthday.value.strftime('%d.%m.%Y')}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            print(f"Contact with name '{name}' not found.")

    def get_upcoming_birthdays(self):
        today = date.today()
        upcoming_birthdays = {}
        for name, record in self.data.items():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday.replace(year=today.year + 1)

                time_to_birthday = birthday_this_year - today
                if 0 <= time_to_birthday.days < 7:
                    day_of_week = (today + time_to_birthday).strftime('%A')
                    if day_of_week not in upcoming_birthdays:
                        upcoming_birthdays[day_of_week] = []
                    upcoming_birthdays[day_of_week].append(name)

        return upcoming_birthdays

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Будь ласка, введіть ім'я та номер телефону.")
    name, phone = args
    record = book.find(name)
    message = "Контакт оновлено."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Контакт додано."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    if len(args) != 3:
        raise ValueError("Будь ласка, введіть ім'я, старий та новий номери телефону.")
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Номер телефону оновлено."
    else:
        raise KeyError

@input_error
def show_phone(args, book: AddressBook):
    if not args:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if record:
        phones = [phone.value for phone in record.phones]
        return ", ".join(phones)
    else:
        raise KeyError

@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Адресна книга порожня."
    result = ""
    for record in book.data.values():
        result += str(record) + "\n"
    return result.strip()

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) != 2:
        raise ValueError("Будь ласка, введіть ім'я та дату народження у форматі ДД.ММ.РРРР.")
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "День народження додано."
    else:
        raise KeyError

@input_error
def show_birthday(args, book: AddressBook):
    if not args:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if record and record.birthday:
        return record.birthday.value.strftime("%d.%m.%Y")
    elif not record:
        raise KeyError
    else:
        return "Для цього контакту не вказано день народження."

@input_error
def upcoming_birthdays(args, book: AddressBook):
    birthdays_next_week = book.get_upcoming_birthdays()
    if not birthdays_next_week:
        return "Наступного тижня днів народжень немає."
    result = "Дні народження на наступному тижні:\n"
    for day, names in birthdays_next_week.items():
        result += f"{day}: {', '.join(names)}\n"
    return result.strip()

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()  # Завантаження даних при запуску
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)  # Збереження даних перед виходом
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(upcoming_birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
