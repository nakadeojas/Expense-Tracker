from datetime import date
from pathlib import Path
import json
import math

DATA_FILE = Path(__file__).parent / "expenses.json"

class Expense:
    def __init__(self, item, amount, category = "", created = None):
        if not isinstance(item, str) or not item.strip():
            raise ValueError("Invalid item name")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise TypeError("Amount must be valid number")
        if amount <= 0 or not math.isfinite(amount):
            raise ValueError("Amount must be a finite number greater than 0")
        if not isinstance(category, str):
            raise TypeError("Invalid category")
        
        self.item = item.strip()
        self.amount = amount
        self.created = created or date.today().isoformat()

        if category.strip() == "":
            self.category = "General"
        else:
            self.category = category.strip()

    def __str__(self):
        return f"{self.item} | {self.category} | ₹{self.amount:.2f} | {self.created}"

    def to_dict(self):
        return {"item" : self.item, "amount" : self.amount, "category" : self.category, "date" : self.created}

    @classmethod
    def from_dict(cls, data):
        return cls(data["item"], data["amount"], data.get("category", ""), created = data.get("date"))

class ExpenseNotFoundError(Exception):
    pass

class ExpenseTracker:
    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.expenses = []

    def add(self, expense):
        self.expenses.append(expense)

    def total(self):
        return sum([expense.amount for expense in self.expenses])

    def total_by_category(self):
        total = {}
        for expense in self.expenses:
            total[expense.category] = total.get(expense.category, 0) + expense.amount

        return total

    def search(self, item):
        item = item.lower()

        return [expense for expense in self.expenses if item in expense.item.lower()]

    def remove(self, number):
        if not isinstance(number, int) or isinstance(number, bool):
            raise TypeError("Enter valid integer") 
        if not (1 <= number <= len(self.expenses)):
            raise ExpenseNotFoundError("Invalid index for expense") 
        
        removed = self.expenses.pop(number - 1)
        return removed

    def __len__(self):
        return len(self.expenses)

    def _backup_file(self):
        backup = self.filename.with_suffix(".bak")
        self.filename.replace(backup)
        return backup

    def save(self):
        data = [expense.to_dict() for expense in self.expenses]
        
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load(self):
        warnings = []
        self.expenses = []
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError:
            backup = self._backup_file()
            warnings.append(f"Data file was damaged. A copy was saved as {backup.name}, starting fresh.")
            return warnings

        if not isinstance(data, list):
            backup = self._backup_file()
            warnings.append("Error: Data not a valid list")
            return warnings

        for position, entry in enumerate(data, start=1):
            try:
                self.expenses.append(Expense.from_dict(entry))
            except KeyError as e:
                warnings.append(f"Entry {position} skipped: missing field {e}")
            except (ValueError, TypeError) as e:
                warnings.append(f"Entry {position} skipped: {e}")

        return warnings

def read_float(prompt):
    while True:
        num = input(prompt).strip()
        try:
            return float(num)
        except ValueError:
            print("Enter a valid number")

def read_int(prompt):
    while True:
        num = input(prompt).strip()
        try:
            return int(num)
        except ValueError:
            print("Please type a whole number, like 3.")

def add_expense(tracker):
    print()
    item = input("Item Name: ").strip()
    amount = read_float("Amount: ")
    category = input("Category: ").strip()

    print()
    try:
        tracker.add(Expense(item, amount, category))
    except (ValueError, TypeError) as e:
        print("Expense not added:", e)
    else:
        tracker.save()
        print("Expense added")

def view_all_expenses(tracker):
    print("\nAll Expenses")
    if not tracker.expenses:
        print("No expenses yet")
    else:
        for index, item in enumerate(tracker.expenses, start=1):
            print(f"{index}. {item}")

def view_total(tracker):
    print(f"\nTotal amount: ₹{tracker.total():.2f}")

def view_total_by_category(tracker):
    print("\nExpenses by Category")
    dic = tracker.total_by_category()

    if not dic:
        print("No expenses yet")
    else:
        for index, (key, value) in enumerate(dic.items(), start=1):
            print(f"{index}. {key} : ₹{value:.2f}")

def remove_an_expense(tracker):
    view_all_expenses(tracker)
    if not tracker.expenses:
        return
    
    print()
    number = read_int("Enter index of item to be removed: ")

    try:
        removed = tracker.remove(number)
    except (TypeError, ExpenseNotFoundError) as e:
        print("Expense not removed:", e)
    else:
        tracker.save()
        print(f"Removed: {removed}")

def search(tracker):
    item = input("\nEnter item name to search: ").strip()

    if not item:
        print("PLease enter a name to search.")
        return

    matches = tracker.search(item)
    if not matches:
        print("No matches")
    else:
        print(f"{len(matches)} match(es) found:")
        for expense in matches:
            print(expense)

def main():
    tracker = ExpenseTracker()

    for warning in tracker.load():
        print("Warning:", warning)

    while True:
        print("\n----- EXPENSE TRACKER -----")
        print("\n1. Add expense")
        print("2. View all expenses")
        print("3. View total")
        print("4. View total by category")
        print("5. Remove an expense")
        print("6. Search expense by name")
        print("7. Quit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_expense(tracker)
        elif choice == "2":
            view_all_expenses(tracker)
        elif choice == "3":
            view_total(tracker)
        elif choice == "4":
            view_total_by_category(tracker)
        elif choice == "5":
            remove_an_expense(tracker)
        elif choice == "6":
            search(tracker)
        elif choice == "7":
            print("\nGoodbye!!!")
            break
        else:
            print("Choose between 1-7")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n\nGoodbye!!!")