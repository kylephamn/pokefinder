import csv
import os

# Define the CSV file name
csv_file = "Pokemon Database.csv"
temp_file = "pokemon_data_temp.csv"

def remove_all_quotes_once():
    """Remove all quotes from every entry in the CSV file (one-time operation)."""
    with open(csv_file, mode='r') as file, open(temp_file, mode='w', newline='') as temp:
        reader = csv.reader(file)
        writer = csv.writer(temp)

        for row in reader:
            # Remove all quotes from each cell
            cleaned_row = [cell.replace('"', '') for cell in row]
            writer.writerow(cleaned_row)

    # Replace the original CSV file with the cleaned version
    os.replace(temp_file, csv_file)
    print("All quotes have been removed from the CSV file.")

# Run the function to remove all quotes
if __name__ == "__main__":
    remove_all_quotes_once()
