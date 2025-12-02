#!/usr/bin/env python3
"""
Replace all phone numbers in ryan_test.csv with test numbers.
Keeps the mobile/work/home structure, only replaces the actual numbers.
Alternates between +14389266456 and +15798819696
"""

import re

INPUT_FILE = "ryan_test.csv"
OUTPUT_FILE = "ryan_test_modified.csv"

TEST_PHONES = ["4389266456", "5798819696"]

def replace_phones_in_line(line, phone_index):
    """Replace ALL phone numbers in the entire line"""
    
    # Pattern to match phone numbers (7+ digits with optional separators)
    # Matches: 4504362433, 514-555-1234, +1 438 926 6456, etc.
    phone_pattern = r'\b(\d[\d\s\-\(\)\+\.]{6,}\d)\b'
    
    def replacer(match):
        nonlocal phone_index
        original = match.group(1)
        # Only replace if it looks like a phone number (at least 10 digits)
        digits_only = re.sub(r'\D', '', original)
        if len(digits_only) >= 10:
            test_phone = TEST_PHONES[phone_index % 2]
            phone_index += 1
            return test_phone
        return original
    
    new_line = re.sub(phone_pattern, replacer, line)
    return new_line, phone_index

def main():
    with open(INPUT_FILE, 'r', encoding='latin-1') as f:
        lines = f.readlines()
    
    new_lines = []
    phone_index = 0
    
    for i, line in enumerate(lines):
        if i == 0:
            # Keep header as-is
            new_lines.append(line)
        else:
            new_line, phone_index = replace_phones_in_line(line, phone_index)
            new_lines.append(new_line)
    
    with open(OUTPUT_FILE, 'w', encoding='latin-1') as f:
        f.writelines(new_lines)
    
    print(f"✅ Created {OUTPUT_FILE}")
    print(f"   - {phone_index} phone numbers replaced")
    print(f"   - Alternating between {TEST_PHONES[0]} and {TEST_PHONES[1]}")

if __name__ == "__main__":
    main()
