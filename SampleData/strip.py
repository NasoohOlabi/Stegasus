import pandas as pd


def copy_csv_without_column(input_file, output_file, column_to_remove):
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(input_file)

    # Drop the specified column from the DataFrame
    if column_to_remove in df.columns:
        df.drop(column_to_remove, axis=1, inplace=True)
    else:
        print("Column not found in the CSV file.")
        return

    # Save the DataFrame as a new CSV file
    df.to_csv(output_file, index=False)

# Usage example
input_filename = './topical_chat.csv'
output_filename = './chats.csv'
column_to_remove = 'sentiment'

copy_csv_without_column(input_filename, output_filename, column_to_remove)

print("CSV copy created without the specified column using pandas.")
