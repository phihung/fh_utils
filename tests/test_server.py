import logging
import shlex
import subprocess
import time
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from threading import Thread

import httpx
import pytest

from fh_utils import serve
from fh_utils.server import _terminate

PORT = 7951
DEMO2_CODE = Path("examples/demo2.py").read_text()
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)


def test_demo2_cli(tmp_path):
    fn = tmp_path / "myapp.py"
    fn.write_text(DEMO2_CODE)

    with run_in_process(fn) as p:
        check_demo2(fn)

    log = p.stdout.read().decode()
    assert log.count("MODEL RELOAD") == 1


def test_demo2_serve(tmp_path, monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.chdir(tmp_path.parent)
    fn = tmp_path / "myapp.py"
    fn.write_text(DEMO2_CODE)
    t = Thread(target=partial(serve, appname=fn, reload_includes=["*.py"], port=PORT))
    t.start()
    try:
        check_demo2(fn)
        captured = capsys.readouterr()
        assert (captured.out + " " + captured.err).count("MODEL RELOAD") == 1
    finally:
        _terminate(5001)
        t.join(2)


def check_demo2(fn):
    client = httpx.Client(base_url=f"http://0.0.0.0:{PORT}")
    for _ in range(2):
        wait_and_test(client, "SAVE")

    fn.write_text(fn.read_text().replace("SAVE", "TADA"))
    time.sleep(2)
    wait_and_test(client, "TADA")


def test_two_files_1(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path.parent)
    fn1, fn2 = tmp_path / "one.py", tmp_path / "two.py"
    fn1.write_text(
        "from fasthtml.common import fast_app\napp, rt = fast_app()\n@app.get('/')\ndef home():\n    return 320 + 1"
    )
    client = httpx.Client(base_url=f"http://0.0.0.0:{PORT}")
    with run_in_process(fn1):
        wait_and_test(client, "321")

        fn2.write_text("def foo():\n    return 120 + 3")
        fn1.write_text("from two import foo\n" + fn1.read_text().replace("320 + 1", "foo()"))
        time.sleep(1)
        wait_and_test(client, "123")

        # fn2.write_text("def foo():\n    return 450 + 6")
        # wait_and_test(client, "456")


def test_two_files_2(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path.parent)
    fn1, fn2 = tmp_path / "one.py", tmp_path / "two.py"
    fn1.write_text(
        "from two import foo\nfrom fasthtml.common import fast_app\napp, rt = fast_app()\n@app.get('/')\ndef home():\n    return foo()"
    )
    fn2.write_text("def foo():\n    return 120 + 3")
    client = httpx.Client(base_url=f"http://0.0.0.0:{PORT}")
    with run_in_process(fn1):
        wait_and_test(client, "123")

        fn2.write_text("def foo():\n    return 450 + 6")
        wait_and_test(client, "456")


def test_three_files(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path.parent)
    fn1, fn2, fn3 = tmp_path / "one.py", tmp_path / "two.py", tmp_path / "three.py"
    fn1.write_text(
        "from two import foo\nfrom fasthtml.common import fast_app\napp, rt = fast_app()\n@app.get('/')\ndef home():\n    return foo()"
    )
    fn2.write_text("from three import bar\ndef foo():\n    return bar()")
    fn3.write_text("def bar():\n    return 120 + 3")
    client = httpx.Client(base_url=f"http://0.0.0.0:{PORT}")
    with run_in_process(fn1):
        wait_and_test(client, "123")

        fn3.write_text("def bar():\n    return 450 + 6")
        wait_and_test(client, "456")


def wait_and_test(client, exp):
    for _ in range(50):
        try:
            if exp in client.get("/").content.decode():
                return
        except httpx.ConnectError:
            pass
        time.sleep(0.2)
    assert exp in client.get("/").content.decode()


@contextmanager
def run_in_process(fn: Path):
    p = subprocess.Popen(
        shlex.split(f"fh_utils dev {fn} --port {PORT}"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=fn.parent.parent,
    )
    try:
        yield p
    except Exception:
        print(p.stdout.read())
        print(p.stdout.read())
    finally:
        p.kill()
