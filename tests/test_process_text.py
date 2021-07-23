from process_text import *
import pytest
import pathlib

this_file_path = str(pathlib.Path(__file__).parent.absolute())

@pytest.fixture
def krisdika_txt():
    return open(this_file_path + "/data/krisdika.txt").read()

def test_remove_symbols():
    assert remove_symbols("● สวัสดี") == " สวัสดี"
    assert remove_symbols("สวัส*ดีโลก") == "สวัสดีโลก"
    assert remove_symbols("สวัสดี•โลก") == "สวัสดีโลก"

def test_remove_number_dot_space():
    assert remove_number_dot_space("1. หวัดดี") == "หวัดดี"

def test_remove_english_in_brackets():
    assert remove_english_in_brackets("เฮลโหล (Hello) เวิรล์ด") == "เฮลโหล เวิรล์ด"

def test_normalize_text():
    assert normalize_text("ช้ี") == "ชี้"

def test_split_sentence():
    assert split_sentence("ฉันทำการบ้าน การบ้านฉันมันยาก") == ['ฉันทำการบ้าน', "การบ้านฉันมันยาก"]

def test_newlines_into_spaces():
    assert split_sentence("ฉันทำ\nการบ้าน\nที่ยาก") == ["ฉันทำ การบ้าน ที่ยาก"]

def test_convert_roman_number_to_word():
    assert number_to_word("พ.ศ. 2497") == "พ.ศ. สองพันสี่ร้อยเก้าสิบเจ็ด"

def test_convert_thai_number_to_word():
    assert number_to_word("พ.ศ. ๒๔๙๗") == "พ.ศ. สองพันสี่ร้อยเก้าสิบเจ็ด"

def test_convert_thai_number_to_word_matches_entire_string():
    assert number_to_word("พ.ศ. ๒๔๙๗.") == "พ.ศ. สองพันสี่ร้อยเก้าสิบเจ็ด."

def test_convert_thai_number_to_word_no_numbers():
    assert number_to_word("ฉันทำการบ้าน") == "ฉันทำการบ้าน"

def test_convert_multiple_numbers_to_words():
    assert number_to_word("มาตรา ๘๔[๔๔]") == "มาตรา แปดสิบสี่[สี่สิบสี่]"

def test_baht_to_words():
    assert baht_to_word("20 บาท") == "ยี่สิบบาท"

def test_expand_maiyamok():
    assert expand_maiyamok("บัญญัติต่าง ๆ") == "บัญญัติต่างต่าง"

def test_expand_maiyamok_without_maiyamok():
    assert expand_maiyamok("บัญญัติต่าง") == "บัญญัติต่าง"

def test_expand_multiple_maiyamoks():
    assert expand_maiyamok("ต่างๆ นาๆ") == "ต่างต่าง นานา"

def test_split_sentence_expand_maiyamok():
    assert expand_maiyamok("บัญญัติต่าง ๆ") == "บัญญัติต่างต่าง"

def test_strip_whitespace():
    assert strip_whitespace(" สวัสดี  วันพุธ ") == "สวัสดี วันพุธ"

def test_remove_commas():
    input = "20,000"
    output = "20000"
    assert remove_symbols(input) == output
    assert split_sentence(input) == ["สองหมื่น"]
