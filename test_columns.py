#!/usr/bin/env python3
import os
import re
import csv
from unicodedata import normalize

COLUMN_CONFIG = {
    "firstname_columns_exact": ["first_name", "firstname", "first", "prenom", "prnom", "given_name", "givenname"],
    "firstname_columns_partial": ["first_name", "firstname", "prenom", "prnom", "given_name"],
    "lastname_columns_exact": ["last_name", "lastname", "last", "nom", "nom_famille", "family_name", "familyname", "surname"],
    "lastname_columns_partial": ["last_name", "lastname", "nom_de_famille", "famille", "family", "surname"],
    "lastname_columns_negative": ["prenom", "first"],
    "phone_columns_exact": ["phone", "telephone", "mobile", "cell", "tel", "phone_number", "phonenumber", "cellphone", "phone1", "phone2", "phone3"],
    "phone_columns_partial": ["phone", "telephone", "mobile", "cell", "tel_", "_tel"],
}

KNOWN_REPLACEMENTS = {
    'Ã©': 'é', 'Ã¨': 'è', 'Ãª': 'ê', 'Ã ': 'à', 'Ã¢': 'â',
    'Ã´': 'ô', 'Ã®': 'î', 'Ã»': 'û', 'Ã§': 'ç', 'Ã¹': 'ù',
}

def fix_french_accents(text):
    for bad, good in KNOWN_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text

def remove_accents(text):
    return "".join(c for c in normalize("NFD", text) if not (0x0300 <= ord(c) <= 0x036f))

def normalize_column_name(name):
    if not name:
        return ""
    name = fix_french_accents(name)
    name = name.replace("\ufffd", "").replace("�", "")
    name = remove_accents(name)
    name = name.lower().strip()
    name = re.sub(r"[\s\-]+", "_", name)
    name = re.sub(r"['\"']", "", name)
    return name

def match_column(col_name, col_type):
    normalized = normalize_column_name(col_name)
    exact_key = f"{col_type}_columns_exact"
    partial_key = f"{col_type}_columns_partial"
    if exact_key in COLUMN_CONFIG and normalized in COLUMN_CONFIG[exact_key]:
        return f"{col_type.upper()} (exact)"
    if partial_key in COLUMN_CONFIG:
        for pattern in COLUMN_CONFIG[partial_key]:
            if pattern in normalized:
                return f"{col_type.upper()} (partial: {pattern})"
    return None

def detect_column(col_name):
    """Detect if a single column is firstname, lastname, or phone."""
    for col_type in ["firstname", "lastname", "phone"]:
        result = match_column(col_name, col_type)
        if result:
            return result
    return "IGNORED"

def detect_columns(headers):
    """Simulate the main app's column detection with the new logic."""
    normalized_headers = [(h, normalize_column_name(h)) for h in headers]
    
    firstname_col = None
    lastname_col = None
    phone_col = None
    
    # First pass: find exact/partial matches
    for original, normalized in normalized_headers:
        if not firstname_col:
            result = detect_column(original)
            if "FIRSTNAME" in result:
                firstname_col = original
        if not lastname_col:
            result = detect_column(original)
            if "LASTNAME" in result:
                lastname_col = original
        if not phone_col:
            result = detect_column(original)
            if "PHONE" in result:
                phone_col = original
    
    # If no firstname found, check for single "name" column
    if not firstname_col:
        name_containing_cols = []
        for original, normalized in normalized_headers:
            if 'name' in normalized:
                # Exclude lastname-like columns
                if not any(x in normalized for x in ['last', 'family', 'famille', 'nom_de_famille']):
                    name_containing_cols.append(original)
        
        if len(name_containing_cols) == 1:
            firstname_col = name_containing_cols[0]
    
    return firstname_col, lastname_col, phone_col

def read_csv_headers(filepath):
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            with open(filepath, "r", encoding=encoding, errors="strict") as f:
                sample = f.read(4096)
                f.seek(0)
                
                # Count occurrences of each delimiter (like main app)
                first_lines = sample.split('\n')[:5]
                header_sample = '\n'.join(first_lines)
                
                separators = [(',', header_sample.count(',')), 
                              (';', header_sample.count(';')), 
                              ('\t', header_sample.count('\t'))]
                separators.sort(key=lambda x: x[1], reverse=True)
                delimiter = separators[0][0] if separators[0][1] > 0 else ','
                
                reader = csv.reader(f, delimiter=delimiter)
                # Skip empty rows to find actual headers
                for row in reader:
                    # Check if row has any non-empty values
                    if any(cell.strip() for cell in row):
                        return row, encoding, delimiter
                return [], encoding, delimiter
        except UnicodeDecodeError:
            continue
    return [], "unknown", ","

def main():
    csv_dir = "test_csv_formats"
    files = sorted([f for f in os.listdir(csv_dir) if f.endswith((".csv", ".txt", ".tsv"))])

    print("=" * 100)
    print("CSV COLUMN DETECTION TEST REPORT")
    print("=" * 100)

    for filename in files:
        filepath = os.path.join(csv_dir, filename)
        headers, encoding, delimiter = read_csv_headers(filepath)
        print(f"\n{'-' * 100}")
        print(f"FILE: {filename}")
        print(f"Encoding: {encoding} | Delimiter: {repr(delimiter)}")
        print(f"Headers ({len(headers)}):")
        
        # Use the new smart detection
        detected_firstname, detected_lastname, detected_phone = detect_columns(headers)
        
        for i, h in enumerate(headers):
            normalized = normalize_column_name(h)
            detection = detect_column(h)
            
            # Check if this is the selected column
            is_selected_firstname = (h == detected_firstname)
            is_selected_lastname = (h == detected_lastname)
            is_selected_phone = (h == detected_phone)
            
            if is_selected_firstname:
                icon = "[FIRST*]"  # * means selected
                if "FIRSTNAME" not in detection:
                    detection = "FIRSTNAME (single 'name' col)"
            elif is_selected_lastname:
                icon = "[LAST*]"
            elif is_selected_phone:
                icon = "[PHONE*]"
            elif "FIRSTNAME" in detection:
                icon = "[FIRST]"
            elif "LASTNAME" in detection:
                icon = "[LAST]"
            elif "PHONE" in detection:
                icon = "[PHONE]"
            else:
                icon = "[----]"
            
            display_h = h[:40] + "..." if len(h) > 40 else h
            print(f"  {icon} [{i}] {display_h:<45} -> {normalized:<30} -> {detection}")
        
        # Final summary
        status = []
        if not detected_firstname:
            status.append("!! NO FIRSTNAME")
        if not detected_lastname:
            status.append("!! NO LASTNAME")
        if not detected_phone:
            status.append("!! NO PHONE")
        if status:
            print(f"  {'  |  '.join(status)}")
        else:
            print(f"  >> SELECTED: firstname='{detected_firstname}' | lastname='{detected_lastname}' | phone='{detected_phone}'")

    print(f"\n{'=' * 100}")
    print("END OF REPORT")

if __name__ == "__main__":
    main()
