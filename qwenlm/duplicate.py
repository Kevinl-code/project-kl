import pandas as pd

# Step 1: Read the Excel file
file_path ="D:\Sheets\PS2.xlsx"  # Replace with your Excel file path
sheet_name ="Sheet1"        # Replace with your sheet name
column_name ="Type_of_Programme"

# Load the Excel file into a DataFrame
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Step 2: Identify duplicates in the specified column
# Keep only the duplicated values (excluding the first occurrence)
duplicates = df[df.duplicated(subset=[column_name], keep='first')][column_name]

# Get unique duplicated values
unique_duplicates = duplicates.unique()

# Step 3: Print the duplicated words
print("Duplicated words in the column:")
for word in unique_duplicates:
    print(word)