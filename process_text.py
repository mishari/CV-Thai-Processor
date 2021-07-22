import re

def remove_symbols(text):
    symbols = ["●","*","•"]
    output = ''.join([c for c in text if c not in symbols])
    return output

def remove_number_dot_space(text):
    output = re.sub(r"\d+\.(\s|$)", "", text)
    return output

def remove_english_in_brackets(text):
    output = re.sub(r"\s\([a-zA-Z ]+\)\s", " ", text)
    return output

def main():
    pass

if __name__ == "__main__":
    main()