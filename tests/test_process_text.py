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
