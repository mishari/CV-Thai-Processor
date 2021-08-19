import re
from pythainlp.util import normalize
from pythainlp.tokenize import sent_tokenize, word_tokenize
from pythainlp.util import num_to_thaiword
import fileinput
import sys
from multiprocessing import Pool
import argparse

import pythaispell

# Parameters from https://github.com/common-voice/sentence-collector/blob/main/server/lib/validation/languages/th.js
MIN_LENGTH = 6
MAX_LENGTH = 100

CV_INVALIDATION = [{
  "regex": '[0-9๐-๙]',
  "error": 'Sentence should not contain numbers',
}, {
  "regex": '[<>+*\\#@^[\]()/\u0E2F\u0E46\u0E4F\u0E5A\u0E5B]',
  "error": 'Sentence should not contain symbols, including Paiyannoi and Maiyamok',
}, {
  "regex": '[A-Za-z]',
  "error": 'Sentence should not contain latin alphabet characters',
}, {
  "regex": '[ก-ฮ]\.[ก-ฮ]+\.',
  "error": 'Sentence should not contain abbreviations',
}, {
  "regex": '(^|\s)[\u0E30\u0E32\u0E33\u0E45\u0E31\u0E34\u0E35\u0E36\u0E37\u0E4D\u0E47\u0E38\u0E39\u0E48\u0E49\u0E4A\u0E4B\u0E3A\u0E4C\u0E4D\u0E4E]',
  "error": 'Word should not start with unexpected characters, like follow vowel and tone mark',
}, {
  "regex": '[\u0E40\u0E41\u0E42\u0E43\u0E44](\s|$)',
  "error": 'Word should not end with leading vowels',
}, {
  "regex": '[\u0E40\u0E41\u0E42\u0E43\u0E44]{2}',
  "error": 'Sentence should not contain repeating lead vowels',
}, {
  "regex": '[\u0E32\u0E33\u0E45]{2}',
  "error": 'Sentence should not contain repeating follow vowels',
}, {
  "regex": '\u0E30{2}',
  "error": 'Sentence should not contain repeating Sara A',
}, {
  "regex": '\u0E3A{2}|\u0E4C{2}|\u0E4D{2}|\u0E4E{2}',
  "error": 'Sentence should not contain repeating Phinthu / Thanthakhat / Nikhahit / Yamakkan',
}, {
  "regex": '[\u0E31\u0E34\u0E35\u0E36\u0E37\u0E4D\u0E47]{2}',
  "error": 'Sentence should not contain repeating above vowels',
}, {
  "regex": '[\u0E38\u0E39]{2}',
  "error": 'Sentence should not contain repeating below vowels',
}, {
  "regex": '[\u0E48\u0E49\u0E4A\u0E4B]{2}',
  "error": 'Sentence should not contain repeating tone marks',
}, {
  "regex": '[\u0E40\u0E41\u0E42\u0E43\u0E44\u0E30\u0E32\u0E33\u0E45][\u0E48\u0E49\u0E4A\u0E4B\u0E3A\u0E4C\u0E4D\u0E4E]',
  "error": 'Sentence should not contain invalid symbols after lead/follow vowels',
}, {
  "regex": '[\u0E48\u0E49\u0E4A\u0E4B\u0E3A\u0E4C\u0E4D\u0E4E][\u0E31\u0E34\u0E35\u0E36\u0E37\u0E4D\u0E47\u0E38\u0E39]',
  "error": 'Sentence should not contain invalid symbols before above/below vowels',
}, {
  "regex": '[\u0E33\u0E45][\u0E30]',
  "error": 'Sentence should not contain Sara A after Sara Am or Lakkhangyao',
}, {
  "regex": '[\u0E30][\u0E32\u0E33\u0E45]',
  "error": 'Sentence should not contain Sara Aa, Sara Am or Lakkhangyao after Sara A',
}, {
  "regex": '[\u200b\u200c\u2063\u0E01-\u0E4E]{71}',
  "error": 'Sentence should not contain more than 70 consonants and vowels running without a space',
}, {
  "regex": """[\u200b\u200c\u2063\u0E01-\u0E4E.,\-"'“”‘’\u0060?!:;]{81}""",
  "error": 'Sentence should not contain more than 80 characters running without a space',
}, {
  "regex": '[\u200b\u200c\u2063ก-ฮ]{31}',
  "error": 'Sentence should not contain more than 30 consonants running without a space',
}, {
  "regex": '(.)\1{6}',
  "error": 'Sentence should not contain more than 7 of the same character in a row',
}, {
  "regex": '(\u00a9|\u00ae|[\u2000-\u3300]|[\u2580-\u27bf]|\ud83c[\ud000-\udfff]|\ud83d[\ud000-\udfff]|\ud83e[\ud000-\udfff]|[\ue000-\uf8ff])',
  "error": 'Sentence should not contain emojis or other special Unicode symbols',
}]

TP_INVALIDATION = [{
  "regex": '\u0E3A',
  "error": 'Sentence should not contain Pinthu as its difficult to read',
}, {
    "regex": r"([ก-ฮ])\1{2,}",
    "error": 'Sentence should not contain three repeating characters',
}]

INVALIDATION = CV_INVALIDATION + TP_INVALIDATION

def is_length_valid(s):
    if len(s) < MIN_LENGTH or len(s) > MAX_LENGTH:
        return False
    else:
        return True

def is_sentence_valid(s):
    rules = INVALIDATION
    valid = True

    if not is_length_valid(s):
        print("INVALID LENGTH: " + s)
        return False

    for r in rules:
        if re.search(r["regex"], s):
            print(r["error"] + ": " + s)
            return False

    return valid

def is_spelling_valid(text):
    spelling = pythaispell.spell(text)

    if text == spelling:
        return True
    else:
        return False

def remove_symbols(text):
    symbols = ["●","*","•","★", "◆",","]
    # From https://stackoverflow.com/questions/33404752/removing-emojis-from-a-string-in-python
    symbols = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
        u"●•★◆" 
        "*"
        ","
                      "]+", re.UNICODE)
    return re.sub(symbols, '', text)

def remove_number_dot_space(text):
    output = re.sub(r"\d+\.(\s|$)", "", text)
    return output

def remove_english_in_brackets(text):
    output = re.sub(r"\s\([a-zA-Z ]+\)\s", " ", text)
    return output

def normalize_text(text):
    return normalize(text)

def repeat_last_word(text):
    words = word_tokenize(text)
    return ''.join(words) + words[-1]

def expand_maiyamok(text):
    return re.sub("([^ๆ]+?)\s*ๆ", lambda x: repeat_last_word(x.group(1)), text)

def strip_whitespace(text):
    text = text.strip()
    text = " ".join(text.split())
    return text

def split_sentence(text):
    tokenized_sentences = sent_tokenize(text)
    tokenized_sentences = [s.replace("\n", " ") for s in tokenized_sentences]
    tokenized_sentences = [remove_symbols(s) for s in tokenized_sentences]
    tokenized_sentences = [remove_english_in_brackets(s) for s in tokenized_sentences]
    tokenized_sentences = [remove_number_dot_space(s) for s in tokenized_sentences]
    tokenized_sentences = [replace_percent(s) for s in tokenized_sentences]
    tokenized_sentences = [number_to_word(s) for s in tokenized_sentences]
    tokenized_sentences = [expand_maiyamok(s) for s in tokenized_sentences]
    tokenized_sentences = [strip_whitespace(s) for s in tokenized_sentences]
    tokenized_sentences = [s.strip('"') for s in tokenized_sentences]
    return tokenized_sentences

def number_to_word(text):
    return re.sub(r"\s*([0-9๐-๙]+)\s*", lambda x: num_to_thaiword(int(x.group(1))), text )

def remove_all_quotes(text):
    return text.replace('"','')

def replace_percent(text):
    return text.replace('%','เปอร์เซ็นต์')

def replace_time(text):
    if re.search("(\d{1,2})[:.](\d{1,2})[-]+(\d{1,2})[:.](\d{1,2})\s?น.", text):
        text = re.sub(r"\s*(\d{1,2})[:.](\d{1,2})[-]+(\d{1,2})[:.](\d{1,2})\s?น.\s*", lambda x: "blah " + x.group(1) + "halb " + x.group(2), text )
        return text
    elif re.search("(\d{1,2})[:.](\d{1,2})\s?น.", text):
        return "match2"
    else:
        return "Match 3"

def second_split_sentence(sentences):
    new_sentences = []
    for n in sentences.split(" "):
        if is_sentence_valid(n):
            n = remove_all_quotes(n)
            n = n.strip('"')
            new_sentences.append(n)
    return new_sentences

def pool_is_spelling_valid(text):
    if is_spelling_valid(text):
        return text
    else:
        return None

def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-i', help='Input file')
    # parser.add_argument('-o', help='Output file')
    # parser.add_argument('-s', help='Perform spell check')
    # args = parser.parse_args()

    input = open(sys.argv[1],"r").read()
    output = open(sys.argv[2],"w")

    inputs = input.split("\n")

    pool = Pool()
    sentences = set()

    for q in pool.imap_unordered(split_sentence,inputs):
        for s in q:
            if is_sentence_valid(s) == True:
                sentences.add(s)
            else:
                try:
                    sentences.update(second_split_sentence(s))
                except ValueError:
                    sentences.add(s)

    # sentences = [x for x in pool.imap_unordered(pool_is_spelling_valid,sentences) if x is not None]

    output.writelines([s + "\n" for s in sentences])

if __name__ == "__main__":
    main()