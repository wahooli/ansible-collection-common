#!/usr/bin/python

from ansible.errors import AnsibleFilterError

def to_pascal_case(text):
    """
    Converts a string to PascalCase (UpperCamelCase).
    - Preserves existing all-caps words (e.g., 'MTU').
    - Does not modify words that already start with a capital (e.g., 'ForwardDelaySec').
    """
    if not isinstance(text, str):
        raise AnsibleFilterError(f"Input must be a string. Received {type(text)}")

    s = text.replace("_", " ").replace("-", " ")
    words = s.split()

    if not words:
        return ""

    processed_words = []
    for word in words:
        # The new, improved logic is here:
        if word.isupper() or word[0].isupper():
            # If the word is all caps (MTU) OR already starts with a capital (ForwardDelaySec),
            # append it without changes.
            processed_words.append(word)
        else:
            # Otherwise, it's a lowercase word that needs capitalizing.
            processed_words.append(word.capitalize())

    return "".join(processed_words)

class FilterModule(object):
    """
    Custom string filters for Ansible.
    """
    def filters(self):
        return {
            'to_pascal_case': to_pascal_case
        }