from process_text import *

def test_remove_symbols():
    assert remove_symbols("● สวัสดี") == " สวัสดี"
    assert remove_symbols("สวัส*ดีโลก") == "สวัสดีโลก"
    assert remove_symbols("สวัสดี•โลก") == "สวัสดีโลก"

def test_remove_number_dot_space():
    assert remove_number_dot_space("1. หวัดดี") == "หวัดดี"