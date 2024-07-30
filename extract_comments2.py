from typing import Dict
import bibtexparser
import glob
from pybtex.database import BibliographyData
from pybtex.database import BibliographyDataError
from pybtex.database import parse_file
from pybtex.database.input import bibtex
import markdown
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import List, Tuple, Iterator, Dict

ColourReset = "\033[0m"
ColourBold = "\033[1m"
Red = "\033[31m"
Green = "\033[32m"
Yellow = "\033[33m"
Blue = "\033[34m"
Magenta = "\033[35m"

ext_key = 'DOC_EXTRACT'
# Regex patterns compiled at module level
# HEADER_PATTERN = re.compile(r'(#+\s.*?)\n', re.DOTALL)
HEADER_PATTERN = re.compile(r'^(#+\s.*?)\n', re.MULTILINE)
INSERT_PATTERN = re.compile(r'\\insert\{(.*?)\}')
LABEL_PATTERN = re.compile(r'\\label\{(.*?)\}')
MATH_EXPR_PATTERN = re.compile(r"(\$\$.*?\$\$)|(\$.*?\$)|(`math\s.*?`)", re.DOTALL)
INLINE_MATH_PATTERN = re.compile(r"(?<!\$)(?<!\\)\$(?!\$)(?!`)(.*?)(?<!`)(?<!\\)\$(?!\$)")
MATH_STAR_PATTERN = re.compile(r"((?<=\$`)(.*?)(?=`\$))|((?<=\$\$)(.*?)(?=\$\$))")

# Reduced multiple calls to `file.read()`


# Initialize an empty bibliography data object
bib_data = BibliographyData()

import bibtexparser
import glob
from pybtex.database import BibliographyData, BibliographyDataError, parse_file

# Initialize an empty bibliography data object
bib_data = BibliographyData()

bib_dir = '/Users/tomoaki/Library/CloudStorage/Dropbox/references/bib_mac_studio/'
input_file_pattern = bib_dir + 'library.bib'
output_file_path = bib_dir + 'unique_references.bib'

def remove_duplicates_and_write(input_files, output_file):
    unique_entries = {}

    for bib_file_path in input_files:
        with open(bib_file_path, 'r') as bib_file:
            bib_database = bibtexparser.load(bib_file)
        
        # Use dictionary comprehension for faster iteration
        unique_entries.update({entry['ID']: entry for entry in bib_database.entries if entry['ID'] not in unique_entries})
    
    new_bib_database = bibtexparser.bibdatabase.BibDatabase()
    new_bib_database.entries = list(unique_entries.values())

    with open(output_file, 'w') as new_bib_file:
        bibtexparser.dump(new_bib_database, new_bib_file)

# Main execution
if False:
    remove_duplicates_and_write(glob.glob(input_file_pattern), output_file_path)

for bib_file in glob.glob(output_file_path):
    try:
        individual_bib_data = parse_file(bib_file)
        for entry_id, entry in individual_bib_data.entries.items():
            if entry_id not in bib_data.entries:
                bib_data.add_entry(entry_id, entry)
    except BibliographyDataError as e:
        print(f"An error occurred while parsing the bibliography file {bib_file}: {e}")

# Continue processing bib_data as before
references = {}

# Function to format author names
# def format_authors(authors: str) -> str:
#     # Splitting the authors by ' and '
#     author_list = authors.split(' and ')

#     # Extracting the surname for each author
#     surname_list = [author.split(',')[0].strip() for author in author_list]

#     if len(surname_list) == 1:
#         return surname_list[0]
#     elif len(surname_list) == 2:
#         return f"{surname_list[0]} and {surname_list[1]}"
#     else:
#         return f"{surname_list[0]} et al."


def format_authors(authors: List[str]) -> str:
    surname_list = []
    for author in authors:
        parts = author.split(',')
        surname = parts[0].strip()  # Assuming surname comes before the comma
        surname_list.append(surname)

    if len(surname_list) == 1:
        return surname_list[0]
    elif len(surname_list) == 2:
        return f"{surname_list[0]} and {surname_list[1]}"
    else:
        return f"{surname_list[0]} et al."


try:
    for entry_id, entry in bib_data.entries.items():
        # Check if the author field exists
        if 'author' in entry.persons:
            authors_list = [str(p) for p in entry.persons['author']]
            author = format_authors(authors_list)
        else:
            author = 'Unknown Author'

        title = entry.fields.get('title')
        year = entry.fields.get('year')
        url = entry.fields.get('url')  # Assumes that the URL field is present

        # Creating the custom reference format
        reference = f"{author} ({year})"
        if url:
            reference = f"[{reference}]({url.split()[0]})"

        if entry_id not in references:
            references[entry_id] = reference
        else:
            print(f"Warning: Repeated entry with key {entry_id}. Ignored.")


except BibliographyDataError as e:
    print(f"An error occurred while parsing the bibliography file: {e}")


def replace_citations(content: str, references: Dict[str, str]) -> str:
    """
    Replaces \cite{citetag} in the content with its corresponding reference if exists
    """
    CITATION_PATTERN = re.compile(r'\\cite\{(.*?)\}')
    return CITATION_PATTERN.sub(lambda m: references.get(m.group(1), m.group()), content)


def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Inserted LABEL_PATTERN in search_labels()


def search_labels(directory: str, extensions: Tuple[str, ...]) -> Dict[str, Tuple[str, int]]:
    labels = {}
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(extensions):
                file_path = os.path.join(dirpath, filename)
                content = read_file_content(file_path)
                for match in LABEL_PATTERN.finditer(content):
                    label = match.group(1)
                    start_line = content[:match.start()].count('\n') + 1
                    labels[label] = (file_path, start_line)
    return labels


INSERT_PATTERN = re.compile(r'\\insert\{(.*?)\}')


def read_file_content(filename: str) -> str:
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return f"<!-- File {filename} not found -->"


def replace_insert_statements(content: str, replacements: Dict[str, str]) -> str:
    """
    Replaces \insert{keyword} in the content with its corresponding replacement if exists.
    If the keyword is a filename, it replaces \insert{filename} with the contents of the file.
    """
    def replace_function(m):
        key = m.group(1)

        # Check if the key is a filename
        if os.path.isfile(key):
            return read_file_content(key)

        # Otherwise, treat it as a specified key
        return replacements.get(key, f"<!-- Key {key} not found -->")

    return INSERT_PATTERN.sub(replace_function, content)


keywords_order = {}


def extract_markdown_comments(input_file: str, content=None) -> Tuple[Dict[str, List[str]], List[Tuple[str, int]]]:
    if content is None:
        with open(input_file, 'r') as file:
            content = file.read()

    markdown_comments = list(CPP_COMMENT_PATTERN.finditer(content)) + list(PYTHON_COMMENT_PATTERN.finditer(content)) + list(MARKDOWN_COMMENT_PATTERN.finditer(content))

    # Initialize dictionary to store comments based on keywords
    keyword_comments = defaultdict(list)
    keyword_info = []
    sec_L_order = []

    for match in markdown_comments:
        comment = match.group(1)
        start_line = content[:match.start()].count('\n') + 1

        # Split comment into lines
        comment_lines = comment.split('\n')

        # Get the minimum number of leading spaces from all lines
        min_indent = min((len(re.match(r'^(\s*)', line).group(1))
                         for line in comment_lines if line.strip()), default=0)

        # Remove leading whitespace from all lines
        comment_lines = [line[min_indent:] for line in comment_lines]
        comment_lines = [line.lstrip() for line in comment_lines]

        # Try to extract "DOC_EXTRACT" keyword from the first line
        doc_extract_pattern = re.compile(r'^' + ext_key + r'\s*(\S*)\s*(\d*)')
        doc_extract_match = doc_extract_pattern.match(comment_lines[0])
        if doc_extract_match:
            keyword = doc_extract_match.group(1).strip() or 'DEFAULT'
            order = int(doc_extract_match.group(
                2)) if doc_extract_match.group(2).isdigit() else 9999
            # Remove the first line from the comment
            comment_lines = comment_lines[1:]
        else:
            keyword = comment_lines[0].split(
            )[0] if comment_lines and comment_lines[0].split() else 'DEFAULT'
            order = 9999

        # if keyword is found in keywords_order, then use the order in keywords_order
        if keyword in keywords_order:
            order = keywords_order[keyword]

        keyword_info.append(keyword)

        # print("comment_lines[0] = ", comment_lines[0], ", keyword = ", keyword, ", order = ", order)

        comment = '\n'.join(comment_lines)
        comment = comment.replace(keyword, '', 1) if keyword != 'DEFAULT' else comment
        cleaned_comment = highlight_keywords(comment)
        cleaned_comment = re.sub(r'!\[(.*?)\]\((.*?)\)', lambda m: f'![{m.group(1)}]({Path(input_file).parent / m.group(2)})', cleaned_comment)
        keyword_comments[(keyword, order)].append(cleaned_comment.strip() + '\n')
        keyword_comments[(keyword, order)].append(f'[{input_file}#L{start_line}]({input_file}#L{start_line})\n')
        # Extract header information for the contents table
        headers = re.findall(HEADER_PATTERN, cleaned_comment)
        for header in headers:
            sec_L_order.append((header.strip(), start_line, order))

    # Sort and group comments based on keyword and order
    sorted_comments = sorted(keyword_comments.items(),
                             key=lambda x: (x[0][0], x[0][1]))
    sorted_comments_dict = {k: v for k, v in sorted_comments}

    sec_L_order = sorted(sec_L_order, key=lambda x: x[1])

    return sorted_comments_dict, sec_L_order, keyword_info


def convert_math_underscore(text: str) -> str:
    math_expr_pattern = r"(\$\$.*?\$\$)|(\$.*?\$)|(`math\s.*?`)"
    matches = list(re.finditer(math_expr_pattern, text, re.DOTALL))
    for match in reversed(matches):
        start, end = match.span()
        # Replace underscores that do not have a space before them
        # Check for non-space characters around the underscore
        new_text = re.sub(r"(?<!\s)_(?!\s)", " _", match.group())
        text = text[:start] + new_text + text[end:]
    return text


def convert_inline_math(text: str) -> str:
    def replace(match):
        math_expr = match.group(1)
        if "`" in math_expr:
            return f"${math_expr}$"
        else:
            return f"$`{math_expr}`$"

    pattern = r"(?<!\$)(?<!\\)\$(?!\$)(?!`)(.*?)(?<!`)(?<!\\)\$(?!\$)"
    return re.sub(pattern, replace, text)


def convert_math_star(text: str) -> str:
    pattern = r"((?<=\$`)(.*?)(?=`\$))|((?<=\$\$)(.*?)(?=\$\$))"
    text = re.sub(pattern, lambda m: m.group().replace(
        "\nabla^*", "\nabla^\\ast").replace("^*", "^\\ast"), text)
    return text


def highlight_keywords(text: str) -> str:
    text = convert_math_underscore(text)
    # text = convert_inline_math(text)
    text = convert_math_star(text)
    keyword_patterns = {
        'NOTE': (r'^NOTE:?\s*', '💡'),
        'SEE': (r'^SEE:?\s*', '👀'),
        'WARNING': (r'^WARNING:?\s*', '⚠️'),
        'TODO': (r'^TODO:?\s*', '📝'),
        'IMPORTANT': (r'^IMPORTANT:?\s*', '❗'),
        'INPROGRESS': (r'^INPROGRESS:?\s*', '🚧'),
        'TIP': (r'^TIP:?\s*', '🌟'),
        'CHECKED': (r'^CHECKED:?\s*', '✅'),
        'UNCHECKED': (r'^UNCHECKED:?\s*', '🟩'),
        'SELECTED': (r'^SELECTED:?\s*', '✅'),
        'UNSELECTED': (r'^UNSELECTED:?\s*', '🟩'),
        'REFERENCE': (r'^REFERENCE:?\s*', '📚'),
        'NOTIMPLEMENTED': (r'NOTIMPLEMENTED:?\s*', '☐'),
        'IMPLEMENTED': (r'IMPLEMENTED?\s*', '☑️'),
        # '###': (r'^###:?\s*', '###'),
        # '##': (r'^## :?\s*', '##'),
        # '#': (r'^# :?\s*', '#'),
        '#': (r'^(#\s+)(.*)', r'\1🤖\2'),
        '##': (r'^(##\s+)(.*)', r'\1⚙️\2'),
        '###': (r'^(###\s+)(.*)', r'\1🔩\2'),
        '####': (r'^(####\s+)(.*)', r'\1🚀 \2'),
    }

    for keyword, (pattern, emoji) in keyword_patterns.items():
        text = re.sub(pattern, f'{emoji} ', text, flags=re.MULTILINE)

    def replace_label(match):
        label = match.group(1)
        text = match.group(2)
        file, line = labels.get(label, ('#', ''))
        return f'[{text}]({file}#L{line})' if file != '#' else f'[{text}](not found)'

    # text = re.sub(r'\\ref\{(.*?)\}\{(.*?)\}', replace_label, text)
    text = re.sub(r'\\ref\{(.*?)\}\{(.*?)\}', replace_label, text)

    # Applying the replace_citations function
    text = replace_citations(text, references)

    return text


def generate_contents_table(sec_L_order: List[Tuple[str, int]], numbered: bool = False) -> str:
    contents_table = '# Contents\n'
    curr_section = 1
    curr_subsection = 0
    curr_subsubsection = 0
    prefix = ''
    for header, line_num, _ in sec_L_order:
        if header.startswith("# "):
            prefix = f"{curr_section}. " if numbered else "- "
            added = f"{prefix}[{header[2:]}](#{header[2:].replace(' ', '-')})\n"
            contents_table += added
            curr_section += 1
            curr_subsection = 0
            # print("added =",added)
        elif header.startswith("## "):
            curr_subsection += 1
            prefix = f"    {curr_section - 1}.{curr_subsection}. " if numbered else "    - "
            added = f"{prefix}[{header[3:]}](#{header[3:].replace(' ', '-')})\n"
            contents_table += added
            curr_subsubsection = 0
            # print("added =",added)
        elif header.startswith("### "):
            curr_subsection += 1
            prefix = f"        {curr_section - 1}.{curr_subsection}. " if numbered else "        - "
            added = f"{prefix}[{header[4:]}](#{header[4:].replace(' ', '-')})\n"
            contents_table += added
            curr_subsubsection = 0
            # print("added =",added)
        elif header.startswith("#### "):
            curr_subsubsection += 1
            prefix = f"            {curr_section - 1}.{curr_subsection}.{curr_subsubsection}. " if numbered else "            - "
            added = f"{prefix}[{header[5:]}](#{header[5:].replace(' ', '-')})\n"
            contents_table += added
            # print("added =",added)
        # print("header =", header)
        # print("prefix =", prefix)

    contents_table += "\n"

    return contents_table


def search_files(directory: str, extensions: Tuple[str, ...]) -> Iterator[str]:
    files = []
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(extensions):
                files.append(os.path.join(dirpath, filename))
    return sorted(files)  # return sorted file paths


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_comments.py output_file search_directory [replacements_directory]")
        sys.exit(1)
    else:
        # display the command line arguments with color
        print(" ".join([Green + arg + ColourReset for arg in sys.argv]))

    output_file = sys.argv[1]
    file_extensions = (".cpp", ".hpp", ".py", ".md")
    search_directory = None
    include_directory = None

    for i in range(2, len(sys.argv)):
        if sys.argv[i] == "-key":
            ext_key = sys.argv[i+1]
        elif sys.argv[i] == "-source":
            search_directory = sys.argv[i+1]
        elif sys.argv[i] == "-include":
            include_directory = sys.argv[i+1]
        else:
            labels = search_labels(sys.argv[i], file_extensions)


    CPP_COMMENT_PATTERN = re.compile(r'/\*' + ext_key + r'(.*?)\*/', re.DOTALL)
    PYTHON_COMMENT_PATTERN = re.compile(r"'''" + ext_key + r" (.*?)'''", re.DOTALL)
    MARKDOWN_COMMENT_PATTERN = re.compile(r'<!--' + ext_key + '-->' + r'(.*?)' + r'<!--' + ext_key + '-->', re.DOTALL)

    all_extracted_comments = defaultdict(list)
    no_keyword_comments = []
    all_sec_L_order = []

    replacements = {}

    # ---------------------------- make keywords_order --------------------------- #
    sorted_keywords = []
    if search_directory is None:
        # errror
        print("Usage: python extract_comments.py output_file search_directory [replacements_directory]")
        sys.exit(1)

    for input_file in sorted(search_files(search_directory, file_extensions)):
        extracted_comments, sec_L_order, keyword_info = extract_markdown_comments(input_file)
        # set keywords_order
        sorted_keywords.extend(keyword_info)

    # delete duplicates and sort sorted_keywords
    sorted_keywords = sorted(list(set(sorted_keywords)))
    # set keywords_order based on sorted_keywords
    for i in range(len(sorted_keywords)):
        keywords_order[sorted_keywords[i]] = i

    # to check
    for i in range(len(keywords_order)):
        print(keywords_order[sorted_keywords[i]], sorted_keywords[i])
    # ---------------------------------------------------------------------------- #

    # If a replacements directory is specified, extract the replacements
    if include_directory is not None:
        for input_file in sorted(search_files(include_directory, file_extensions)):
            extracted_comments, _, __ = extract_markdown_comments(input_file)
            for keyword, comments in extracted_comments.items():
                # Comment replacement should be the content
                replacements[keyword[0]] = ' '.join(comments)

    for input_file in sorted(search_files(search_directory, file_extensions)):
        content = read_file_content(input_file)
        content = replace_insert_statements(content, replacements)
        extracted_comments, sec_L_order, keyword_info = extract_markdown_comments(input_file, content)

        if extracted_comments:
            for keyword, comments in extracted_comments.items():
                if keyword == 'DEFAULT':
                    no_keyword_comments.extend(comments)
                else:
                    all_extracted_comments[keyword].extend(comments)

            all_sec_L_order.extend(sec_L_order)

    contents_table = generate_contents_table(sorted(all_sec_L_order, key=lambda sec_line_order: sec_line_order[2])) + "\n---\n"

    # Sorting the extracted comments by the order number
    sorted_extracted_comments = sorted(all_extracted_comments.items(), key=lambda keyword_comments: keyword_comments[0][1])

    with open(output_file, 'w') as md_file:
        md_file.write(contents_table)
        for (keyword, order), comments in sorted_extracted_comments:
            md_file.write("\n".join(comments))
            md_file.write("\n---\n")  # Horizontal line after the entire group
        for comment in no_keyword_comments:
            md_file.write(comment)
            # Horizontal line after each comment without a keyword
            md_file.write("\n---\n")
