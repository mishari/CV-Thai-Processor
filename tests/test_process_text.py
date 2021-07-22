from process_text import remove_symbols

def test_remove_symbols():
    assert remove_symbols("● สวัสดี") == " สวัสดี"
    assert remove_symbols("สวัส*ดีโลก") == "สวัสดีโลก"
    assert remove_symbols("สวัสดี•โลก") == "สวัสดีโลก"