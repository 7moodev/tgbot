import os
import re
# A script to convert naming conventions
def camel_to_snake(name):
    """Convert camelCase to snake_case."""
    s1 = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    return s1.lower()

def convert_to_snake_case(content):
    """Convert all camelCase identifiers in the Python script to snake_case."""
    def replace_match(match):
        word = match.group()
        return camel_to_snake(word)

    # Match variable, function, and argument names (but avoid string contents and comments)
    pattern = re.compile(r'\b[a-z]+(?:[A-Z][a-z]*)+\b')
    return pattern.sub(replace_match, content)

def process_file(file_path):
    """Read a file, convert its content to snake_case, and overwrite the file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        converted_content = convert_to_snake_case(content)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(converted_content)
        print(f"Processed: {file_path}")
    except Exception as e:
        print(f"Failed to process {file_path}: {e}")

def process_directory(directory_path):
    """Recursively process all Python files in a directory and its subdirectories."""
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                process_file(file_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Convert camelCase to snake_case in Python files.")
    parser.add_argument("directory", type=str, help="Path to the directory containing Python files.")
    args = parser.parse_args()

    process_directory(args.directory)
