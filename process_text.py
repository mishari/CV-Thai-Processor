
def remove_symbols(text):
    symbols = ["●","*","•"]
    output = ''.join([c for c in text if c not in symbols])
    return output

def main():
    pass

if __name__ == "__main__":
    main()