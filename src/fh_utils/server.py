import enum
import importlib
import inspect
import logging
import os
import sys
import threading
import time
from dataclasses import dataclass
from functools import lru_cache, wraps
from pathlib import Path

import uvicorn
from uvicorn.supervisors.watchfilesreload import FileFilter
from watchfiles import watch

logger = logging.getLogger()


class CliException(Exception): ...


class ReloadType(str, enum.Enum):
    NO_RELOAD = "no"
    FULL = "full"
    FAST = "fast"


_IN_FAST_RELOAD = [False]
_ATTR_NO_RELOAD = "_norl"


def serve(
    appname: Path | None = None,
    app: str = "app",
    host="0.0.0.0",
    port: int | None = None,
    reload: ReloadType = ReloadType.FAST,
    reload_includes: list[str] | str | None = None,
    reload_excludes: list[str] | str | None = None,
    **kwargs,
):
    """Drop in replacement for fasthtml.core.serve with default for fast-reload"""
    port = port or int(os.getenv("PORT", default=5001))
    path = Path(appname or inspect.stack()[1].filename)
    serve_dev(
        path=path,
        app=app,
        host=host,
        port=port,
        reload=reload,
        reload_includes=reload_includes,
        reload_excludes=reload_excludes,
        **kwargs,
    )


def serve_prod(path: Path, app: str, host: str, port: int, **kwargs):
    _, use_uvicorn_app = _get_import_string(path=path, app_name=app)
    use_kwargs = dict(app=use_uvicorn_app, host=host, port=port, **kwargs)
    uvicorn.run(**use_kwargs, reload=False)


def serve_dev(
    path: Path,
    app: str,
    host: str,
    port: int,
    live: bool = False,
    reload: ReloadType = ReloadType.FAST,
    **kwargs,
):
    module_import_str, use_uvicorn_app = _get_import_string(path=path, app_name=app)
    use_kwargs = dict(app=use_uvicorn_app, host=host, port=port, **kwargs)
    if live and reload != ReloadType.FAST:
        raise CliException("--live only supported in fast reload mode")
    if reload == ReloadType.NO_RELOAD:
        uvicorn.run(**use_kwargs, reload=False)
    elif reload == ReloadType.FULL:
        uvicorn.run(**use_kwargs, reload=True)
    elif reload == ReloadType.FAST:
        try:
            _IN_FAST_RELOAD[0] = True
            _run_with_fast_reload(
                module_import_str, app_str=app, host=host, port=port, live=live, **kwargs
            )
        finally:
            _IN_FAST_RELOAD[0] = False
    else:
        raise Exception(reload)


def _run_with_fast_reload(
    module_import_str: str, app_str: str, port: int, host: str, live: bool, **kwargs
):
    try:
        from fasthtml.jupyter import nb_serve, wait_port_free
        from IPython.extensions.autoreload import ModuleReloader
    except ImportError:  # pragma: no cover
        raise CliException("Needs ipython installed: pip install ipython")
    _patch_autoreload()

    module = importlib.import_module(module_import_str)
    reloader = ModuleReloader()
    reloader._report = print

    use_kwargs = {
        **kwargs,
        "port": port,
        "host": host,
        "log_level": None,
        "reload": False,
        "reload_dirs": None,
        "reload_includes": None,
        "reload_excludes": None,
    }

    def server_reload(server):
        reloader.check(True)
        if server:
            server.should_exit = True
            wait_port_free(port, host=host)
            time.sleep(0.2)
        app = getattr(module, app_str)
        if live:
            _add_live_reload(app)
        return nb_serve(app, **use_kwargs)

    global watcher
    global server

    server = server_reload(None)
    watcher = Watcher(**kwargs)
    try:
        for changes in watcher.loop():
            logger.warning(
                "WatchFiles detected changes in %s. Reloading...",
                ", ".join(map(_display_path, changes)),
            )
            server = server_reload(server)
    finally:
        _terminate(port)


watcher, server = None, None


def _terminate(port):
    from fasthtml.jupyter import wait_port_free

    global watcher
    global server
    if watcher is not None:
        watcher.shutdown()
        watcher = None
    if server is not None:
        server.should_exit = True
        wait_port_free(port)
        server = None


def no_reload_cache(user_function):
    """lru_cache but can survive fast reloading. No cost outside reloading mode."""
    return no_reload(lru_cache(maxsize=None)(user_function))


def no_reload(func):
    """Wrap the function to make it unaffected by fast reloading. No cost outside reloading mode."""
    if not _IN_FAST_RELOAD[0]:
        return func
    setattr(func, _ATTR_NO_RELOAD, True)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@dataclass
class _ModuleData:
    module_import_str: str
    extra_sys_path: Path


def _get_module_data_from_path(path: Path) -> _ModuleData:
    use_path = path.resolve()
    module_path = use_path
    if use_path.is_file() and use_path.stem == "__init__":
        module_path = use_path.parent
    module_paths = [module_path]
    extra_sys_path = module_path.parent
    for parent in module_path.parents:
        init_path = parent / "__init__.py"
        if init_path.is_file():
            module_paths.insert(0, parent)
            extra_sys_path = parent.parent
        else:
            break
    module_str = ".".join(p.stem for p in module_paths)
    return _ModuleData(module_import_str=module_str, extra_sys_path=extra_sys_path.resolve())


def _get_import_string(*, path: Path, app_name: str = "app") -> str:
    if not path.exists():
        raise CliException(f"Path does not exist {path}")
    mod_data = _get_module_data_from_path(path)
    sys.path.insert(0, str(mod_data.extra_sys_path))
    import_string = f"{mod_data.module_import_str}:{app_name}"
    return mod_data.module_import_str, import_string


def _patch_autoreload():
    from IPython.extensions import autoreload

    def update_function(old, new):
        """Upgrade the code object of a function"""
        autoreload.update_function(old, new)

        if hasattr(old, _ATTR_NO_RELOAD) and hasattr(new, _ATTR_NO_RELOAD):
            old_closure, new_closure = old.__closure__, new.__closure__
            if len(old_closure) != len(new_closure):
                return
            for o, n in zip(old_closure, new_closure):
                n.cell_contents = o.cell_contents

    autoreload.UPDATE_RULES[1] = (autoreload.UPDATE_RULES[1][0], update_function)
    autoreload.UPDATE_RULES[3] = (
        autoreload.UPDATE_RULES[3][0],
        lambda a, b: update_function(a.__func__, b.__func__),
    )


def _display_path(path: Path) -> str:
    try:
        return f"'{path.relative_to(Path.cwd())}'"
    except ValueError:  # pragma: no cover
        return f"'{path}'"


class Watcher:
    def __init__(self, **kwargs) -> None:
        # We try to mimic as much as possible uvicorn behavior
        config = uvicorn.Config("dummy", **{**kwargs, "log_level": "critical", "reload": True})
        reload_dirs = []
        for directory in config.reload_dirs:
            if Path.cwd() not in directory.parents:
                reload_dirs.append(directory)
        if Path.cwd() not in reload_dirs:
            reload_dirs.append(Path.cwd())

        self.should_exit = threading.Event()
        self.watcher = watch(
            *reload_dirs,
            watch_filter=None,
            stop_event=self.should_exit,
            yield_on_timeout=True,
            raise_interrupt=False,
        )
        self.watch_filter = FileFilter(config)

    def loop(self):
        for changes in self.watcher:
            unique_paths = {Path(c[1]) for c in changes}
            changes = [p for p in unique_paths if self.watch_filter(p)]
            if changes:
                yield changes

    def shutdown(self):
        self.should_exit.set()


def _add_live_reload(app):
    if hasattr(app, "LIVE_RELOAD_HEADER"):
        return

    from fasthtml.live_reload import LIVE_RELOAD_SCRIPT, FastHTMLWithLiveReload, Script

    rt = FastHTMLWithLiveReload.LIVE_RELOAD_ROUTE
    app.LIVE_RELOAD_HEADER = Script(
        LIVE_RELOAD_SCRIPT.format(
            reload_attempts=1,
            reload_interval=1000,
        )
    )
    app.hdrs.append(app.LIVE_RELOAD_HEADER)
    app.router.add_ws(rt.path, rt.endpoint)
