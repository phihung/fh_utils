import shlex
from unittest.mock import MagicMock, patch

from inline_snapshot import snapshot
from typer.testing import CliRunner

from fh_utils.cli import app

runner = CliRunner()


def test_smoke():
    assert runner.invoke(app, ["--version"]).exit_code == 0
    assert runner.invoke(app, ["--help"]).exit_code == 0
    assert runner.invoke(app, ["dev", "--help"]).exit_code == 0


@patch("fh_utils.server.serve_dev")
def test_dev(mock: MagicMock):
    cmd = "dev src/app.py --reload fast --port 8000 --log-level error --reload-include src"
    runner.invoke(app, shlex.split(cmd))
    assert repr(mock.call_args_list[0]).replace("PosixPath", "Path") == snapshot(
        "call(path=Path('src/app.py'), app='app', host='0.0.0.0', port=8000, reload=<ReloadType.FAST: 'fast'>, live=False, log_level='error', reload_includes=('src',))"
    )
    mock.assert_called_once()


@patch("fh_utils.server.serve_dev")
def test_dev__default(mock: MagicMock):
    cmd = "dev src/app.py"
    runner.invoke(app, shlex.split(cmd))
    assert repr(mock.call_args_list[0]).replace("PosixPath", "Path") == snapshot(
        "call(path=Path('src/app.py'), app='app', host='0.0.0.0', port=5001, reload=<ReloadType.FAST: 'fast'>, live=False)"
    )
    mock.assert_called_once()


@patch("fh_utils.server.serve_dev")
def test_dev__wrong_argument(mock: MagicMock):
    cmd = "dev src/app.py --reload-incl src"
    assert runner.invoke(app, shlex.split(cmd)).exit_code != 0
    mock.assert_not_called()


@patch("fh_utils.server.serve_prod")
def test_prod(mock: MagicMock):
    cmd = "run src/app.py --port 8000 --log-level error"
    runner.invoke(app, shlex.split(cmd))
    assert repr(mock.call_args_list[0]).replace("PosixPath", "Path") == snapshot(
        "call(path=Path('src/app.py'), app='app', host='0.0.0.0', port=8000, log_level='error')"
    )
    mock.assert_called_once()


@patch("fh_utils.server.serve_prod")
def test_prod__default(mock: MagicMock):
    cmd = "run src/app.py"
    runner.invoke(app, shlex.split(cmd))
    assert repr(mock.call_args_list[0]).replace("PosixPath", "Path") == snapshot(
        "call(path=Path('src/app.py'), app='app', host='0.0.0.0', port=5001)"
    )
    mock.assert_called_once()


@patch("fh_utils.server.serve_prod")
def test_prod__wrong_argument(mock: MagicMock):
    cmd = "run src/app.py --reload-incl src"
    assert runner.invoke(app, shlex.split(cmd)).exit_code != 0
    mock.assert_not_called()
