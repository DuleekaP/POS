import pandas as pd

def rename_duplicates(file_path, sheet_name, column_name, output_file):
    # Load Excel file
    df = pd.read_excel(file_path, sheet_name=sheet_name)

    # Dictionary to track occurrences of each value
    count_dict = {}

    # List to store modified values
    new_values = []

    for value in df[column_name]:
        if pd.isna(value):  # Skip NaN values
            new_values.append(value)
            continue

        if value in count_dict:
            count_dict[value] += 1
            new_value = f"{value}-({count_dict[value]})"
        else:
            count_dict[value] = 0
            new_value = value

        new_values.append(new_value)

    # Assign the modified values to a new column
    df[f"{column_name}_Unique"] = new_values

    # Save the updated DataFrame to a new Excel file
    df.to_excel(output_file, index=False)
    print(f"Updated file saved as: {output_file}")

# Example Usage
file_path = "RING SET.xlsx"  # Replace with your file name
sheet_name = "Sheet1"  # Adjust as needed
column_name = "PRODUCT  ID"  # Change to the column you want to process
output_file = "piston_updated.xlsx"  # New file name

rename_duplicates(file_path, sheet_name, column_name, output_file)