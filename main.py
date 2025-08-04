import random
import re

NUMBER_PATTERN = r'##[0-9]{22}'

def random_number_string(match=None):
    return f"##{random.randint(10**21, 10**22 - 1)}"

def random_number_lines(num_lines=5):
    return [random_number_string() for _ in range(num_lines)]

def ensure_number_lines(text, num_lines=5):
    lines = text.splitlines()
    head_lines = lines[:num_lines]
    tail_lines = lines[-num_lines:]

    need_head = not all(re.match(NUMBER_PATTERN, l.strip()) for l in head_lines)
    need_tail = not all(re.match(NUMBER_PATTERN, l.strip()) for l in tail_lines)

    new_lines = []
    if need_head:
        new_lines += random_number_lines(num_lines)
    new_lines += lines
    if need_tail:
        new_lines += random_number_lines(num_lines)

    return '\n'.join(new_lines)

def replace_numbers(text):
    import re
    return re.sub(NUMBER_PATTERN, random_number_string, text)

def main():
    print("⭐ Cargando")

if __name__ == "__main__":
    main()
