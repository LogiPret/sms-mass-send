#!/usr/bin/env python3
"""Remove single-line comments from JavaScript file, except header comments"""

import sys

def remove_comments(input_file, output_file=None):
    """Remove all lines starting with // except the first 3 header lines"""
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Keep first 3 header comment lines
    result_lines = []
    header_comments_kept = 0
    
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        
        # Keep the first 3 comment lines (header)
        if stripped.startswith('//') and header_comments_kept < 3:
            result_lines.append(line)
            header_comments_kept += 1
        # Remove all other comment-only lines
        elif stripped.startswith('//'):
            continue
        # Keep all non-comment lines
        else:
            result_lines.append(line)
    
    # Write to output file or same file
    output = output_file or input_file
    with open(output, 'w', encoding='utf-8') as f:
        f.writelines(result_lines)
    
    print(f"Removed comments from {input_file}")
    print(f"Output written to {output}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python remove_comments.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    remove_comments(input_file, output_file)
