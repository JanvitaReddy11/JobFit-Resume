import json
import subprocess

def escape_latex_special_chars(text):
    special_chars = {
        '%': r'\%',
        '&': r'\&',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '$': r'\$',
        '^': r'\textasciicircum{}',
        '~': r'\textasciitilde{}',
        '"': r"''",
        "'": r"'",
        "-": r"-",
        "--": r"--",
        "---": r"---",
        "’": r"\textquotesingle{}",
        "–": r"--",
        "—": r"---",
        "«": r"``",
        "»": r"''",
    }

    for char, replacement in special_chars.items():
        text = text.replace(char, replacement)
    return text



def process_json(data):

    if isinstance(data, dict):
        return {escape_latex_special_chars(key): process_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [process_json(item) for item in data]
    elif isinstance(data, str):
        return escape_latex_special_chars(data)
    else:
        return data

