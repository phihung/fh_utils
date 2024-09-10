from fh_utils.tailwind import TAILWIND_DAISYCSS_CONFIG, tailwind_compile

_ = """
Div(cls="p-16")
Div(cls="step step-primary")
"""


def test_compile__default(tmp_path):
    fn = tmp_path / "a/app.css"
    tailwind_compile(fn)
    assert fn.exists()
    assert "p" + "-16" in fn.read_text()
    assert "p" + "-1.5" not in fn.read_text()
    assert "ste" + "p-primary" not in fn.read_text()


def test_compile__daisy(tmp_path):
    fn = tmp_path / "app.css"
    tailwind_compile(str(fn), cfg=TAILWIND_DAISYCSS_CONFIG)
    assert fn.exists()
    print(fn.read_text())
    assert "p" + "-16" in fn.read_text()
    assert "p" + "-1.5" not in fn.read_text()
    assert "ste" + "p-primary" in fn.read_text()
    assert "ste" + "p-secondary" not in fn.read_text()
