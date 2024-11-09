import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import csv
import difflib
import sys
import os
import requests # type: ignore
import data
import remove
from PIL import Image, ImageTk # type: ignore
from io import BytesIO

# Define the CSV file names
simple_csv = "Pokemon.csv"
complex_csv = "Pokemon Database.csv"

def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS.
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def initialize_csv(csv_file):
    """Initialize the CSV file with headers if it doesn't exist."""
    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if csv_file == "Pokemon.csv":
                headers = ["ID", "Name", "Form", "Type1", "Type2", "Total", "HP", "Attack",
                           "Defense", "Sp. Atk", "Sp. Def", "Speed", "Generation"]
            else:
                headers = ["Pokemon Id", "Pokedex Number", "Pokemon Name",
                           "Classification", "Alternate Form Name", "Original Pokemon ID",
                           "Legendary Type", "Pokemon Height", "Pokemon Weight",
                           "Primary Type", "Secondary Type", "Primary Ability",
                           "Primary Ability Description", "Secondary Ability",
                           "Secondary Ability Description", "Hidden Ability",
                           "Hidden Ability Description", "Special Event Ability",
                           "Special Event Ability Description", "Male Ratio",
                           "Female Ratio", "Base Happiness", "Game(s) of Origin",
                           "Health Stat", "Attack Stat", "Defense Stat",
                           "Special Attack Stat", "Special Defense Stat", "Speed Stat",
                           "Base Stat Total", "Health EV", "Attack EV", "Defense EV",
                           "Special Attack EV", "Special Defense EV", "Speed EV",
                           "EV Yield Total", "Catch Rate", "Experience Growth",
                           "Experience Growth Total", "Primary Egg Group",
                           "Secondary Egg Group", "Egg Cycle Count",
                           "Pre-Evolution Pokemon Id", "Evolution Details"]
            writer.writerow(headers)

def find_closest_name(input_name, names):
    """Find the most similar name to the input_name using difflib."""
    closest_match = difflib.get_close_matches(
        input_name.lower(), [name.lower() for name in names], n=1, cutoff=0.4
    )
    return closest_match[0] if closest_match else None

def fetch_pokemon_sprite(pokemon_name):
    """Fetch and display the sprite of a Pokémon from the PokéAPI."""
    api_name = pokemon_name.lower().replace(' ', '-').replace('.', '').replace("'", '').replace(":", '')
    url = f"https://pokeapi.co/api/v2/pokemon/{api_name}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        sprite_url = data["sprites"]["front_default"]
        if sprite_url:
            image_response = requests.get(sprite_url)
            img_data = Image.open(BytesIO(image_response.content))
            img = ImageTk.PhotoImage(img_data)
            # Display the image in a new window
            sprite_window = tk.Toplevel()
            sprite_window.title(f"{pokemon_name} Sprite")
            tk.Label(sprite_window, image=img).pack()
            # Keep a reference to the image to prevent garbage collection
            sprite_window.img = img
        else:
            messagebox.showinfo("No Sprite", f"No sprite found for {pokemon_name}.")
    else:
        messagebox.showerror("API Error", f"PokéAPI request failed for {pokemon_name}.")

def prompt_form_selection(forms, name_key, form_key):
    """Prompt the user to select which form(s) they want to see."""
    print("\nMultiple forms found:")
    for index, form in enumerate(forms, start=1):
        form_name = form.get(form_key, 'Standard') if form_key else 'Standard'
        print(f"{index}. {form[name_key]} - {form_name}")

    while True:
        selected_index = input("Enter the number of the form you want to see (or 'all' to view all, 'b' to go back): ").strip().lower()
        if selected_index == 'all':
            for form in forms:
                display_form_data(form, name_key)
            break
        elif selected_index == 'b':
            # Go back to the previous menu
            return False  # Indicate to go back
        elif selected_index.isdigit() and 1 <= int(selected_index) <= len(forms):
            selected_form = forms[int(selected_index) - 1]
            display_form_data(selected_form, name_key)
            break
        else:
            print("Invalid selection. Please try again.")

def display_form_data(form, name_key):
    """Display the CSV data of the selected Pokémon form."""
    print("\nForm Details:")
    for key, value in form.items():
        print(f"{key}: {value}")

    choice = input(f"Would you like to see the sprite for {form[name_key]}? (y/n): ").strip().lower()
    if choice == 'y':
        fetch_pokemon_sprite(form[name_key])

def add_entry(csv_file):
    """Add a new entry to the selected CSV file."""
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Read the headers to prompt user input dynamically
        with open(csv_file, mode='r', newline='', encoding='utf-8') as read_file:
            reader = csv.reader(read_file)
            headers = next(reader)

        print("Enter the details for the new Pokémon entry (enter 'b' to go back):")
        new_entry = {}
        for header in headers:
            value = input(f"{header}: ").strip()
            if value.lower() == 'b':
                return  # Go back to the main menu
            new_entry[header] = value

        # Ensure that the new entry has values for all headers
        entry_row = [new_entry.get(header, '') for header in headers]
        writer.writerow(entry_row)
        print("Entry added successfully!")

def retrieve_entry(csv_file):
    """Retrieve entries with advanced filtering options."""
    if not os.path.exists(csv_file):
        print(f"The CSV file {csv_file} does not exist.")
        return

    while True:
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames

            # Determine the correct keys based on the CSV headers
            if "Name" in headers:
                # Simple database
                name_key = "Name"
                type_key1 = "Type1"
                type_key2 = "Type2"
                id_key = "ID"
                form_key = "Form" if "Form" in headers else None
            else:
                # Complex database
                name_key = "Pokemon Name"
                type_key1 = "Primary Type"
                type_key2 = "Secondary Type"
                id_key = "Pokemon Id"
                form_key = "Alternate Form Name"

            criteria_options = ["id", "name", "type"]
            if form_key:
                criteria_options.append("form")

            criteria_prompt = ", ".join([option.capitalize() for option in criteria_options])
            criteria = input(f"Search by ({criteria_prompt}, or 'b' to go back): ").strip().lower()
            if criteria == 'b':
                return  # Go back to the main menu
            if criteria not in criteria_options:
                print("Invalid search criteria.")
                continue

            value = input(f"Enter the {criteria} to search for (or 'b' to go back): ").strip().lower()
            if value == 'b':
                continue  # Go back to the retrieval menu

            # Reset the reader to the beginning of the file
            file.seek(0)
            reader = csv.DictReader(file)

            matching_forms = []
            names_list = []

            for row in reader:
                names_list.append(row[name_key])
                matches = False

                if criteria == "id" and row[id_key].strip().lower() == value:
                    matches = True
                elif criteria == "name" and row[name_key].strip().lower() == value:
                    matches = True
                elif criteria == "type" and (
                    value == row[type_key1].strip().lower() or value == row.get(type_key2, '').strip().lower()
                ):
                    matches = True
                elif criteria == "form" and form_key and row[form_key].strip().lower() == value:
                    matches = True

                if matches:
                    matching_forms.append(row)

            if matching_forms:
                if len(matching_forms) > 1:
                    back = prompt_form_selection(matching_forms, name_key, form_key)
                    if back is False:
                        continue  # Go back to the retrieval menu
                else:
                    display_form_data(matching_forms[0], name_key)
            else:
                # If no exact match, suggest the closest name
                closest_name = find_closest_name(value, names_list)
                if closest_name:
                    confirm = input(f"No exact match found. Did you mean '{closest_name}'? (y/n): ").strip().lower()
                    if confirm == 'y':
                        value = closest_name.lower()
                        # Reset the reader to the beginning of the file
                        file.seek(0)
                        reader = csv.DictReader(file)
                        matching_forms = []

                        for row in reader:
                            if row[name_key].strip().lower() == value:
                                matching_forms.append(row)

                        if matching_forms:
                            if len(matching_forms) > 1:
                                back = prompt_form_selection(matching_forms, name_key, form_key)
                                if back is False:
                                    continue  # Go back to the retrieval menu
                            else:
                                display_form_data(matching_forms[0], name_key)
                        else:
                            print(f"No matching entry found for name = {value}.")
                    else:
                        print("No matching entry found.")
                else:
                    print(f"No matching entry found for {criteria} = {value}.")

def select_database():
    """Prompt the user to select between Simple and Complex databases."""
    while True:
        print("\nSelect the database to use:")
        print("1. Simple (Pokemon.csv)")
        print("2. Complex (Pokemon Database.csv)")
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            self.csv_file = resource_path("Pokemon.csv") # type: ignore
        elif choice == "2":
            self.csv_file = resource_path("Pokemon Database.csv") # type: ignore
        else:
            print("Invalid choice. Please try again.")

def main():
    """Main function to run the program."""
    csv_file = select_database()
    initialize_csv(csv_file)

    while True:
        print("\nOptions:")
        print("1. Add a new Pokémon entry")
        print("2. Retrieve an entry")
        print("3. Change Database")
        print("4. Exit")

        choice = input("Enter your choice: ").strip()
        if choice == "1":
            add_entry(csv_file)
        elif choice == "2":
            retrieve_entry(csv_file)
        elif choice == "3":
            # Re-select the database
            csv_file = select_database()
            initialize_csv(csv_file)
        elif choice == "4":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

class PokemonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokémon Data Application")
        self.csv_file = None
        self.initialize_gui()

    def initialize_gui(self):
        # Main menu frame
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=20)

        tk.Label(self.menu_frame, text="Pokémon Data Application", font=("Helvetica", 16)).pack(pady=10)

        # Buttons for options
        tk.Button(self.menu_frame, text="Select Database", command=self.select_database).pack(pady=5)
        tk.Button(self.menu_frame, text="Add New Pokémon Entry", command=self.add_entry).pack(pady=5)
        tk.Button(self.menu_frame, text="Retrieve Entry", command=self.retrieve_entry).pack(pady=5)
        tk.Button(self.menu_frame, text="Exit", command=self.root.quit).pack(pady=5)

    def select_database(self):
        choice = simpledialog.askstring("Select Database", "Enter 1 for Simple or 2 for Complex Database:")
        if choice == "1":
            self.csv_file = "Pokemon.csv"
        elif choice == "2":
            self.csv_file = "Pokemon Database.csv"
        else:
            messagebox.showerror("Invalid Choice", "Please enter 1 or 2.")
            return

        # Initialize the CSV file
        initialize_csv(self.csv_file)
        messagebox.showinfo("Database Selected", f"Database set to {self.csv_file}")

    def add_entry(self):
        if not self.csv_file:
            messagebox.showwarning("No Database Selected", "Please select a database first.")
            return

        with open(self.csv_file, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)

            with open(self.csv_file, mode='r', newline='', encoding='utf-8') as read_file:
                reader = csv.reader(read_file)
                headers = next(reader)

            new_entry = []
            for header in headers:
                value = simpledialog.askstring("Add Entry", f"Enter {header}:")
                if value is None:
                    messagebox.showinfo("Cancelled", "Entry addition cancelled.")
                    return
                new_entry.append(value.strip())

            writer.writerow(new_entry)
            messagebox.showinfo("Success", "Entry added successfully!")

    def retrieve_entry(self):
        if not self.csv_file:
            messagebox.showwarning("No Database Selected", "Please select a database first.")
            return

        # Open the CSV file
        with open(self.csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            headers = reader.fieldnames

            # Determine keys based on headers
            if "Name" in headers:
                name_key = "Name"
                type_key1 = "Type1"
                type_key2 = "Type2"
                id_key = "ID"
                form_key = "Form" if "Form" in headers else None
            else:
                name_key = "Pokemon Name"
                type_key1 = "Primary Type"
                type_key2 = "Secondary Type"
                id_key = "Pokemon Id"
                form_key = "Alternate Form Name"

            # Get search criteria
            criteria_options = ["id", "name", "type"]
            if form_key:
                criteria_options.append("form")

            criteria = simpledialog.askstring("Search Entry", f"Search by ({', '.join(criteria_options)}):")
            if criteria is None or criteria.lower() not in criteria_options:
                messagebox.showerror("Invalid Input", "Invalid search criteria.")
                return

            value = simpledialog.askstring("Search Entry", f"Enter the {criteria}:")
            if value is None:
                return

            value = value.strip().lower()
            file.seek(0)
            reader = csv.DictReader(file)

            matching_forms = []
            names_list = []

            for row in reader:
                names_list.append(row[name_key])
                matches = False

                if criteria == "id" and row[id_key].strip().lower() == value:
                    matches = True
                elif criteria == "name" and row[name_key].strip().lower() == value:
                    matches = True
                elif criteria == "type" and (
                    value == row[type_key1].strip().lower() or value == row.get(type_key2, '').strip().lower()
                ):
                    matches = True
                elif criteria == "form" and form_key and row[form_key].strip().lower() == value:
                    matches = True

                if matches:
                    matching_forms.append(row)

            if matching_forms:
                if len(matching_forms) > 1:
                    self.prompt_form_selection(matching_forms, name_key, form_key)
                else:
                    self.display_form_data(matching_forms[0], name_key)
            else:
                closest_name = find_closest_name(value, names_list)
                if closest_name:
                    confirm = messagebox.askyesno("No Exact Match", f"Did you mean '{closest_name}'?")
                    if confirm:
                        value = closest_name.lower()
                        file.seek(0)
                        reader = csv.DictReader(file)
                        matching_forms = []

                        for row in reader:
                            if row[name_key].strip().lower() == value:
                                matching_forms.append(row)

                        if matching_forms:
                            if len(matching_forms) > 1:
                                self.prompt_form_selection(matching_forms, name_key, form_key)
                            else:
                                self.display_form_data(matching_forms[0], name_key)
                        else:
                            messagebox.showinfo("Not Found", f"No matching entry found for name = {value}.")
                    else:
                        messagebox.showinfo("Not Found", "No matching entry found.")
                else:
                    messagebox.showinfo("Not Found", f"No matching entry found for {criteria} = {value}.")

    def prompt_form_selection(self, forms, name_key, form_key):
        options = []
        for index, form in enumerate(forms, start=1):
            form_name = form.get(form_key, 'Standard') if form_key else 'Standard'
            options.append(f"{form[name_key]} - {form_name}")

        selected = simpledialog.askstring("Select Form", f"Multiple forms found:\n" +
                                          "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options)) +
                                          "\nEnter the number of the form you want to view:")

        if selected is None:
            return
        if selected.isdigit() and 1 <= int(selected) <= len(forms):
            selected_form = forms[int(selected) - 1]
            self.display_form_data(selected_form, name_key)
        else:
            messagebox.showerror("Invalid Selection", "Please enter a valid number.")
            self.prompt_form_selection(forms, name_key, form_key)

    def display_form_data(self, form, name_key):
        data_str = "\n".join(f"{key}: {value}" for key, value in form.items())
        messagebox.showinfo("Pokémon Data", data_str)

        choice = messagebox.askyesno("Show Sprite", f"Would you like to see the sprite for {form[name_key]}?")
        if choice:
            fetch_pokemon_sprite(form[name_key])

def main():
    root = tk.Tk()
    app = PokemonGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()