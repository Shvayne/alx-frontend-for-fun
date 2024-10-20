#!/usr/bin/env python3
"""
Script to convert Markdown to HTML with support for headings, unordered lists, ordered lists, paragraphs, bold text,
and special syntax for MD5 and character removal.
"""

import sys
import os
import re
import hashlib  # Import hashlib module to generate MD5 hash

def convert_markdown_to_html(markdown_file, output_file):
    """Converts Markdown content to HTML, handling headings, unordered lists, ordered lists, paragraphs, bold text, and special syntax."""
    try:
        with open(markdown_file, 'r') as md_file, open(output_file, 'w') as html_file:
            in_unordered_list = False  # Flag to track unordered list
            in_ordered_list = False  # Flag to track ordered list
            in_paragraph = False  # Flag to track paragraphs

            for line in md_file:
                stripped_line = line.strip()

                # Check if the line is a heading
                if stripped_line.startswith('#'):
                    heading_level = len(stripped_line.split(' ')[0])
                    heading_text = stripped_line[heading_level:].strip()
                    if in_unordered_list:  # Close unordered list if it was open
                        html_file.write('</ul>\n')
                        in_unordered_list = False
                    if in_ordered_list:  # Close ordered list if it was open
                        html_file.write('</ol>\n')
                        in_ordered_list = False
                    if in_paragraph:  # Close paragraph if it was open
                        html_file.write('</p>\n')
                        in_paragraph = False
                    heading_text = process_special_syntax(heading_text)
                    heading_text = parse_bold_text(heading_text)
                    html_file.write(f'<h{heading_level}>{heading_text}</h{heading_level}>\n')

                # Check if the line is an unordered list item
                elif stripped_line.startswith('- '):
                    list_item_text = stripped_line[2:].strip()
                    if not in_unordered_list:  # Open a new unordered list if not already inside one
                        if in_paragraph:  # Close paragraph if it was open
                            html_file.write('</p>\n')
                            in_paragraph = False
                        html_file.write('<ul>\n')
                        in_unordered_list = True
                    list_item_text = process_special_syntax(list_item_text)
                    list_item_text = parse_bold_text(list_item_text)
                    html_file.write(f'    <li>{list_item_text}</li>\n')

                # Check if the line is an ordered list item
                elif stripped_line.startswith('* '):
                    list_item_text = stripped_line[2:].strip()
                    if not in_ordered_list:  # Open a new ordered list if not already inside one
                        if in_paragraph:  # Close paragraph if it was open
                            html_file.write('</p>\n')
                            in_paragraph = False
                        html_file.write('<ol>\n')
                        in_ordered_list = True
                    list_item_text = process_special_syntax(list_item_text)
                    list_item_text = parse_bold_text(list_item_text)
                    html_file.write(f'    <li>{list_item_text}</li>\n')

                # Handle paragraphs
                elif stripped_line:
                    if not in_paragraph:  # Start a new paragraph if not already inside one
                        if in_unordered_list:  # Close unordered list if it was open
                            html_file.write('</ul>\n')
                            in_unordered_list = False
                        if in_ordered_list:  # Close ordered list if it was open
                            html_file.write('</ol>\n')
                            in_ordered_list = False
                        html_file.write('<p>\n')
                        in_paragraph = True
                    else:
                        html_file.write('    <br/>\n')  # Add a line break for new lines within a paragraph
                    line_with_special_syntax = process_special_syntax(stripped_line)
                    line_with_bold = parse_bold_text(line_with_special_syntax)
                    html_file.write(f'    {line_with_bold}\n')

                else:  # Handle empty lines that may indicate the end of a paragraph
                    if in_paragraph:
                        html_file.write('</p>\n')
                        in_paragraph = False

            # Ensure any open lists or paragraphs are closed at the end of the file
            if in_unordered_list:
                html_file.write('</ul>\n')
            if in_ordered_list:
                html_file.write('</ol>\n')
            if in_paragraph:
                html_file.write('</p>\n')

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def parse_bold_text(text):
    """
    Replaces **text** with <b>text</b> and __text__ with <em>text</em> using regular expressions.
    """
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)  # Replace **text** with <b>text</b>
    text = re.sub(r'__(.+?)__', r'<em>\1</em>', text)  # Replace __text__ with <em>text</em>
    return text

def process_special_syntax(text):
    """
    Processes special syntax for:
    - [[text]] to convert text to its MD5 hash (lowercase).
    - ((text)) to remove all 'c' characters (case-insensitive) from the text.
    """
    # Convert [[text]] to its MD5 hash
    text = re.sub(r'\[\[(.+?)\]\]', lambda match: hashlib.md5(match.group(1).encode()).hexdigest(), text)

    # Remove all 'c' characters (case-insensitive) from ((text))
    text = re.sub(r'\(\((.+?)\)\)', lambda match: match.group(1).replace('c', '').replace('C', ''), text)

    return text

def main():
    """Main function to handle command-line arguments and call the conversion function."""
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)

    markdown_file = sys.argv[1]
    output_file = sys.argv[2]

    if not os.path.isfile(markdown_file):
        print(f"Missing {markdown_file}", file=sys.stderr)
        sys.exit(1)

    convert_markdown_to_html(markdown_file, output_file)
    sys.exit(0)

if __name__ == "__main__":
    main()
