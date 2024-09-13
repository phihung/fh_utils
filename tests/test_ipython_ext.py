from testbook import testbook


@testbook("examples/extension.ipynb", execute=True)
def test_example(tb):
    assert tb.get("count") == 1234
