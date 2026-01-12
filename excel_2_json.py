import pandas as pd
import json

def excel_to_json(excel_file, json_file, sheet_name=0):
    try:
        # 1. Read the Excel file
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df = df.fillna('')

        # 2. Convert DataFrame to a list of dictionaries (Python objects)
        data_dict = df.to_dict(orient='records')

        # 3. Use the standard json library to write the file
        # ensure_ascii=False handles special characters
        # The standard library does NOT escape forward slashes by default
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, indent=4, ensure_ascii=False)
        
        print(f"Success! '{excel_file}' converted. Slashes like '/' are preserved.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Usage
excel_to_json('card_faces.xlsx', 'card_faces.json', 'card_faces')
# excel_to_json('card_faces.xlsx', 'card_faces.json', 'card_faces')
# excel_to_json('card_faces.xlsx', 'card_faces.json', 'card_faces')