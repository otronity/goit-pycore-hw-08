import re
import pickle
from collections import UserDict
from datetime import datetime, timedelta, date

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, name):
        self.value = name

class Phone(Field):
    def __init__(self, phone):
        super().__init__(phone)  
        if bool(re.match(r'^\d{10}$', phone)):
            self.value = phone
        else:
            raise ValueError('Incorrect Phone number')

    # Изменяем номер телефона с проверкой на корректность нового номера   
    def change_phone(self, phone):
        if bool(re.match(r'^\d{10}$', phone)):
            self.value = phone
        else:
            raise ValueError('Incorrect New Phone number')

class Birthday(Field):
    def __init__(self, value):
         # Регулярное выражение для проверки формата DD.MM.YYYY
        pattern = r'^\d{2}\.\d{2}\.\d{4}$'
        if re.match(pattern, value):
            try:
                datetime.strptime(value, "%d.%m.%Y").date()
                self.value = value #datetime.strptime(value, "%d.%m.%Y").date() 
            except ValueError:
                raise ValueError("Invalid date format. Use DD.MM.YYYY")  
        else:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")  
               

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
            
    def add_phone(self, phone):
        if not any(p.value == phone for p in self.phones):
            self.phones.append(Phone(phone))

    def edit_phone(self, phoneold, phonenew):
        # перевіряємо чи є номер який хочемо змінити в переліку телефонів
        if not any(p.value == phoneold for p in self.phones):
            raise ValueError(f'Incorrect Phone number {phoneold}')
        for phone in self.phones:
            if phone.value == phoneold:
                # перевіряємо чи є новий номер вже в перліку телефонів
                if not any(p.value == phonenew for p in self.phones):
                    phone.change_phone(phonenew)
                else:
                    self.remove_phone(phoneold)
                break

    def find_phone(self, phone):
        result = list(filter(lambda record: record.value == phone, self.phones))
        return result[0] if len(result) > 0 else None
    
    def remove_phone(self, phone):
        phonedel = self.find_phone(phone)
        if phonedel:
            self.phones.remove(phonedel)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):        
        self.data[record.name.value] = record

    def find(self, name):
        result = list(filter(lambda record: record.name.value == name, self.data.values()))
        return result[0] if len(result) > 0 else None
    
    def delete(self, name):
        del self.data[name]

    def __str__(self):
        if not self.data:
            return "Address Book is empty."

        contacts_str = "\n".join([f"{record.name.value}: {', '.join(p.value for p in record.phones) if record.phones else 'No phones'} birthday: {record.birthday if record.birthday else 'not added'}"
                                 for record in self.data.values()])
        return f"Address Book:\n{contacts_str}"
    
    def string_to_date(self,date_string):
        return datetime.strptime(date_string, "%d.%m.%Y").date()

    def date_to_string(self, date):        
        return date.strftime("%d.%m.%Y")

    def find_next_weekday(self, start_date, weekday):
        days_ahead = weekday - start_date.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return start_date + timedelta(days=days_ahead)

    def adjust_for_weekend(self, birthday):
        if birthday.weekday() >= 5:
            return self.find_next_weekday(birthday, 0) 
        else:
            return birthday
        
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = date.today()
        days = 7
        for record in self.data.values():            
            if record.birthday:
                birthday = self.string_to_date(record.birthday.value)
                birthday_this_year = self.adjust_for_weekend(birthday.replace(year=today.year))
                if birthday_this_year < today:
                    birthday_this_year = self.adjust_for_weekend(birthday.replace(year=today.year + 1))
                if birthday_this_year <= self.find_next_weekday(today, days) and birthday_this_year >= today:
                    upcoming_birthdays.append({"name": record.name.value, "birthday": self.date_to_string(birthday_this_year)}) 
        return upcoming_birthdays
    
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                return "Not enough parameters."
            else:
                return str(e)
        except Exception as e:  # Обработка любых исключений
            return f"Error: {e}"
    return inner
    
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    # Знаходження та редагування телефону для контакту
    name, phone, phonenew, *_ = args
    record = book.find(name)
    message = "Phone updated."
    if record is None:
        message = "Contact not exists."
    else:
        record.edit_phone(phone, phonenew)
    return message

@input_error
def show_phone(args, book: AddressBook):
    # Знаходження та редагування телефону для контакту
    name, *_ = args
    record = book.find(name)
    message = ''
    if record is None:
        message = "Contact not exists."
    else:
        for phone in record.phones:
            message += f'{phone} \n'
    return message

@input_error
def add_birthday(args, book):
    # додаємо до контакту день народження в форматі DD.MM.YYYY
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        message = "Contact not exists."
    else:
        record.add_birthday(birthday)
        message = "Birthday added."
    return message

@input_error
def show_birthday(args, book):
    # показуємо день народження контакту
    name, *_ = args
    record = book.find(name)
    message = ""
    if record is None:
        message = "Contact not exists."
    elif record.birthday:
        message = f'Birthday is {record.birthday}'
    else:
        message = f'Birthday is not added to {name}'
    return message

@input_error
def birthdays(args, book):
    # повертає список користувачів, яких потрібно привітати по днях на наступному тижні
    message = ""
    birthdays = book.get_upcoming_birthdays()
    if birthdays:
        for record in book.get_upcoming_birthdays():
            message += f'Name: {record["name"]}  congrat day: {record["birthday"]}\n'
    else:
        message = "There are no birthdays in the next 7 days"
    return message

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def save_data(book, filename):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено
        
def main():
    filename="addressbook.pkl"
    book = load_data(filename) #AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book, filename)
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
            print(book)

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
