import re

def add_backslash(match):
    char = match.group(0)
    if char == '"':
        return r'\"'
    elif char == "'":
        return r"\'"
    elif char == "\\":
        return r"\\"

def sanitise_input(input_string):
    pattern = r'[\\\'"]'
    return re.sub(pattern, add_backslash, input_string)
