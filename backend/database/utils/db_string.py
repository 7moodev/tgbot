import re

def camel_to_snake(name):
    """Convert camelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    return s2.lower()


def convert_to_snake_case(content):
    """Convert all camelCase identifiers in the Python script to snake_case."""

    def replace_match(match):
        word = match.group()
        return camel_to_snake(word)

    # Match variable, function, and argument names (but avoid string contents and comments)
    pattern = re.compile(r"\b[a-zA-Z][a-zA-Z0-9]*\b")
    return pattern.sub(replace_match, content)


def pluralize(noun):
    """Convert a singular noun to its plural form."""
    if re.search("[sxz]$", noun):
        return re.sub("$", "es", noun)
    elif re.search("[^aeioudgkprt]h$", noun):
        return re.sub("$", "es", noun)
    elif re.search("[aeiou]y$", noun):
        return re.sub("y$", "ys", noun)
    elif re.search("[^aeiou]y$", noun):
        return re.sub("y$", "ies", noun)
    else:
        return noun + "s"

def lower_first_letter(s):
    return s[:1].lower() + s[1:]
