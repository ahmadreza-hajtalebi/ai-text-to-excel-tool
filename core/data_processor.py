import pandas as pd
import os
import csv

def process_ai_data(input_file_path, output_file_path, num_columns, ignore_extra_delimiters=False):
    """
    Processes raw text data from a file, standardizes it, and saves it to an Excel file.
    It now handles duplicate headers and extra delimiters gracefully.

    Args:
        input_file_path (str): The path to the raw text input file.
        output_file_path (str): The path for the output Excel file.
        num_columns (int): The number of columns to expect in the data.
        ignore_extra_delimiters (bool): Flag to ignore extra delimiters and put content in the last column.
    
    Returns:
        tuple[pd.DataFrame, list]: A tuple containing the DataFrame and a list of warnings, or (None, None) on failure.
    """
    DELIMITER = '%'
    warnings = []
    processed_data = []
    
    # 1. Check if the input file exists
    if not os.path.exists(input_file_path):
        warnings.append(f"Error: Input file '{input_file_path}' not found.")
        return None, warnings

    with open(input_file_path, 'r', encoding='utf-8') as f:
        # 2. Read the header line and process it
        header_line = f.readline().strip()
        headers = header_line.split(DELIMITER)
        
        if len(headers) != num_columns:
            warnings.append(f"Error: Mismatch between expected columns ({num_columns}) and headers in file ({len(headers)}).")
            return None, warnings
            
        # 3. Read and process the rest of the data lines
        for line_num, line in enumerate(f, start=2): # Start counting from line 2
            stripped_line = line.strip()
            if not stripped_line:
                continue

            # --- New logic for handling duplicate headers ---
            parts_for_check = stripped_line.split(DELIMITER)
            if parts_for_check == headers:
                warnings.append(f"Warning: Skipping repeated header row on line {line_num}.")
                continue

            # --- New logic for handling extra delimiters based on user flag ---
            if ignore_extra_delimiters:
                # Use maxsplit to put all extra content into the last column
                parts = stripped_line.split(DELIMITER, maxsplit=num_columns - 1)
                
                # Check if there were extra delimiters and warn the user
                if stripped_line.count(DELIMITER) > num_columns - 1:
                    warnings.append(f"Warning on line {line_num}: Extra delimiters found. Extra content was added to the last column.")
            else:
                # Standard split without maxsplit
                parts = stripped_line.split(DELIMITER)
            
            if len(parts) == num_columns:
                try:
                    row_dict = dict(zip(headers, parts))
                    processed_data.append(row_dict)
                except Exception as e:
                    warnings.append(f"Error creating dictionary for line {line_num}: {e}")
            else:
                warnings.append(f"Error on line {line_num}: Mismatch in column count. Expected {num_columns}, found {len(parts)}. Row: '{stripped_line}'")
    
    if not processed_data:
        warnings.append("No valid data found to process.")
        return None, warnings

    # 4. Create a DataFrame and save to Excel
    try:
        df = pd.DataFrame(processed_data)
        df.to_excel(output_file_path, index=False, engine='openpyxl')
        warnings.append(f"Data successfully saved to '{output_file_path}'.")
        return df, warnings
    except Exception as e:
        warnings.append(f"Error saving to Excel file: {e}")
        return None, warnings

# --- How to use this script (This part will be updated by the GUI) ---
if __name__ == "__main__":
    # Example usage, simulating inputs from the GUI
    INPUT_FILENAME = '../data/input_data.txt'
    OUTPUT_FILENAME = '../data/output_data.xlsx'
    COLUMNS = 4
    IGNORE_EXTRA_DELIMITERS = True # Example flag
    
    # The function now returns a tuple of (DataFrame, warnings)
    df, all_warnings = process_ai_data(INPUT_FILENAME, OUTPUT_FILENAME, COLUMNS, IGNORE_EXTRA_DELIMITERS)
    
    if all_warnings:
        print("\n--- Processing Report ---")
        for w in all_warnings:
            print(w)