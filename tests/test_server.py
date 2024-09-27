import logging
import os
import shlex
import signal
import subprocess
import sys
import time
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from threading import Thread
from unittest.mock import patch

import httpx
import pytest
from inline_snapshot import snapshot

from fh_utils import serve
from fh_utils.server import _terminate, serve_prod

PORT = 7951
DEMO2_CODE = Path("examples/demo2.py").read_text()
client = httpx.Client(base_url=f"http://0.0.0.0:{PORT}")
logging.getLogger("uvicorn.error").setLevel(logging.CRITICAL)


def test_demo2_cli(tmp_path):
    fn = tmp_path / "myapp.py"
    fn.write_text(DEMO2_CODE)

    with run_in_process(fn) as p:
        check_demo2(p, fn)

    log = p.stdout.read().decode()
    assert log.count("MODEL RELOAD") == 1


def test_demo2_serve(tmp_path, capsys):
    fn = tmp_path / "myapp.py"
    fn.write_text(DEMO2_CODE)
    t = Thread(target=partial(serve, appname=fn, reload_includes=["*.py"], port=PORT, live=True))
    t.start()
    try:
        check_demo2(None, fn)
        captured = capsys.readouterr()
        assert (captured.out + " " + captured.err).count("MODEL RELOAD") == 1
    finally:
        _terminate(5001)
        t.join(2)


def check_demo2(p, fn):
    for _ in range(2):
        wait_and_test(p, "SAVE")

    fn.write_text(fn.read_text().replace("SAVE", "TADA"))
    time.sleep(2)
    wait_and_test(p, "TADA")


def test_two_files_1(tmp_path):
    fn1, fn2 = tmp_path / "one.py", tmp_path / "two.py"
    fn1.write_text(
        "from fasthtml.common import fast_app\napp, rt = fast_app()\n@app.get('/')\ndef home():\n    return 320 + 1"
    )
    with run_in_process(fn1) as p:
        wait_and_test(p, "321")

        fn2.write_text("def foo():\n    return 120 + 3")
        fn1.write_text("from two import foo\n" + fn1.read_text().replace("320 + 1", "foo()"))
        time.sleep(1)
        wait_and_test(p, "123")

        # fn2.write_text("def foo():\n    return 450 + 6")
        # wait_and_test(p, "456")


def test_two_files_2(tmp_path):
    fn1, fn2 = tmp_path / "one.py", tmp_path / "two.py"
    fn1.write_text(
        "from two import foo\nfrom fasthtml.common import fast_app\napp, rt = fast_app()\n@app.get('/')\ndef home():\n    return foo()"
    )
    fn2.write_text("def foo():\n    return 120 + 3")
    with run_in_process(fn1) as p:
        wait_and_test(p, "123")

        fn2.write_text("def foo():\n    return 450 + 6")
        wait_and_test(p, "456")


def test_three_files(tmp_path):
    fn1, fn2, fn3 = tmp_path / "one.py", tmp_path / "two.py", tmp_path / "three.py"
    fn1.write_text(
        "from two import foo\nfrom fasthtml.common import fast_app\napp, rt = fast_app()\n@app.get('/')\ndef home():\n    return foo()"
    )
    fn2.write_text("from three import bar\ndef foo():\n    return bar()")
    fn3.write_text("def bar():\n    return 120 + 3")
    with run_in_process(fn1) as p:
        wait_and_test(p, "123")

        fn3.write_text("def bar():\n    return 450 + 6")
        wait_and_test(p, "456")


@pytest.mark.parametrize(
    "args",
    ["--live", "--live --app get_app", "--live --app get_app --factory"],
    ids="012",
)
@pytest.mark.skip("Unstable")
def test_live(args, tmp_path):
    fn1 = tmp_path / "one.py"
    fn1.write_text(
        "from fasthtml.common import fast_app, Div\napp, rt = fast_app()\n@app.get('/')\ndef home():\n    return Div(120 + 3)\ndef get_app():\n    return app"
    )
    with run_in_process(fn1, args=args) as p:
        wait_and_test(p, "123")
        wait_and_test(p, "WebSocket")
        fn1.write_text(fn1.read_text().replace("120 + 3", "450 + 6"))
        wait_and_test(p, "456")
        wait_and_test(p, "WebSocket")


def test_prod_cli():
    with run_in_process(Path("examples/demo2.py"), cmd="run") as p:
        wait_and_test(p, "SAVE")


@patch("uvicorn.run")
def test_serve_prod(mock):
    serve_prod(Path("examples/demo2.py"), "app", "127.0.0.1", 1234)
    assert repr(mock.call_args_list[0]) == snapshot(
        "call(app='demo2:app', host='127.0.0.1', port=1234, reload=False)"
    )
    mock.assert_called_once()


@patch("uvicorn.run")
def test_dev_no_reload(mock):
    serve(reload="no")
    assert repr(mock.call_args_list[0]) == snapshot(
        "call(app='tests.test_server:app', host='0.0.0.0', port=5001, reload_includes=None, reload_excludes=None, reload=False)"
    )
    mock.assert_called_once()


@patch("uvicorn.run")
def test_dev_full_reload(mock):
    serve(reload="full")
    assert repr(mock.call_args_list[0]) == snapshot(
        "call(app='tests.test_server:app', host='0.0.0.0', port=5001, reload_includes=None, reload_excludes=None, reload=True)"
    )
    mock.assert_called_once()


def wait_and_test(p, exp):
    for _ in range(50):
        if p and p.poll() is not None:
            break
        try:
            if exp in client.get("/").content.decode():
                return
        except httpx.ConnectError:
            pass
        time.sleep(0.2)
    assert exp in client.get("/").content.decode()


@contextmanager
def run_in_process(fn: Path, cmd="dev", args=""):
    print(f"fh_utils.cli {cmd} {fn} --port {PORT} {args}")
    p = subprocess.Popen(
        shlex.split(f"{sys.executable} -m fh_utils.cli {cmd} {fn} --port {PORT} {args}"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        yield p
    except Exception:
        print(p.stdout.read().decode())
        print(p.stderr.read().decode())
        raise
    finally:
        os.kill(p.pid, signal.SIGINT)
        p.wait(1)
        p.terminate()
        p.wait(1)
        p.kill()
        p.wait(1)
    assert p.returncode is not None
    assert p.returncode != 1
