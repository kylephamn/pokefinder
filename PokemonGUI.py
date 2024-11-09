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

def resource_path(relative_path):
    """Get the absolute path to the resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS.
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Define the initialize_csv function
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

# Define the find_closest_name function
def find_closest_name(input_name, names):
    """Find the most similar name to the input_name using difflib."""
    closest_matches = difflib.get_close_matches(
        input_name.lower(), [name.lower() for name in names], n=1, cutoff=0.6
    )
    return closest_matches[0] if closest_matches else None

class PokemonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pokémon Data Application")
        self.csv_file = None
        self.center_window(self.root, 400, 300)  # Center the main window with desired dimensions
        self.initialize_gui()

    def center_window(self, window, width, height):
        """Center the given window on the screen."""
        # Get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        # Calculate x and y coordinates
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')

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
            self.csv_file = resource_path("Pokemon.csv")
        elif choice == "2":
            self.csv_file = resource_path("Pokemon Database.csv")
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
        # Create a new window to display the Pokémon data
        data_window = tk.Toplevel()
        data_window.title(f"{form[name_key]} Data")

        # Frame for the content
        content_frame = tk.Frame(data_window)
        content_frame.pack(pady=10, padx=10)

        # Fetch and display the sprite
        sprite = self.fetch_pokemon_sprite(form[name_key])

        if sprite:
            img_label = tk.Label(content_frame, image=sprite)
            img_label.image = sprite  # Keep a reference to avoid garbage collection
            img_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

        # Display the data in a text widget
        data_str = "\n".join(f"{key}: {value}" for key, value in form.items())
        text_widget = tk.Text(content_frame, wrap='word', width=60, height=25)
        text_widget.grid(row=0, column=1, padx=10, pady=10)
        text_widget.insert('1.0', data_str)
        text_widget.config(state='disabled')  # Make the text widget read-only

        # Frame for the buttons
        button_frame = tk.Frame(content_frame)
        button_frame.grid(row=1, column=1, pady=5, sticky='e')

        # Retrieve Another button
        retrieve_another_button = tk.Button(button_frame, text="Retrieve Another", command=lambda: [data_window.destroy(), self.retrieve_entry()])
        retrieve_another_button.pack(side='left', padx=5)

        # Close button
        close_button = tk.Button(button_frame, text="Close", command=data_window.destroy)
        close_button.pack(side='left', padx=5)

    def fetch_pokemon_sprite(self, pokemon_name):
        """Fetch and return the sprite of a Pokémon from the PokéAPI."""
        api_name = pokemon_name.lower().replace(' ', '-').replace('.', '').replace("'", '').replace(":", '')
        url = f"https://pokeapi.co/api/v2/pokemon/{api_name}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            sprite_url = data["sprites"]["front_default"]
            if sprite_url:
                image_response = requests.get(sprite_url)
                img_data = image_response.content
                img = Image.open(BytesIO(img_data))
                photo = ImageTk.PhotoImage(img)
                return photo
            else:
                messagebox.showinfo("No Sprite", f"No sprite found for {pokemon_name}.")
                return None
        else:
            messagebox.showinfo("API Error", f"PokéAPI request failed for {pokemon_name}.")
            return None

def main():
    root = tk.Tk()
    app = PokemonGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
