#!/usr/bin/env python3
import sys

def generate_code(first, last):
    f_init = first[0].upper()
    l_init = last[0].upper()
    
    # Count letters only
    letters = len(''.join(c for c in first + last if c.isalpha()))
    base = (letters * 69) % 1000
    
    # Add alphabet positions (A=1, B=2, etc.)
    f_pos = ord(f_init) - ord('A') + 1
    l_pos = ord(l_init) - ord('A') + 1
    
    # Second block: keep only 3 digits with modulo
    suffix = (f_pos * 100 + l_pos) % 1000
    
    return f'{f_init}{l_init}-{base:03d}-{suffix:03d}'

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./generate_code.py FirstName LastName")
        print("Example: ./generate_code.py Hugo Otth")
        sys.exit(1)
    
    first = sys.argv[1]
    last = sys.argv[2]
    code = generate_code(first, last)
    print(code)
