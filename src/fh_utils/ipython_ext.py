try:
    from IPython.core.magic import needs_local_scope, register_line_magic
    from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
    from IPython.display import IFrame, Pretty, display
except ImportError:
    pass

import socket
import threading
import time
from contextlib import closing

import uvicorn

PORT_RANGE = range(5011, 5111)


def load_ipython_extension(ipython):
    reloader = JupyterReloader()

    @magic_arguments()
    @argument("app", help="Name of fast_app instance.")
    @argument("--page", default="/", help="Uri of the page to display")
    @argument("-w", "--width", default="100%", help="Iframe width in percentage or in pixels")
    @argument("-h", "--height", default="500", help="Iframe height in percentage or in pixels")
    @argument(
        "-p", "--port", default=None, help="Will start the server on this port (if available)"
    )
    @register_line_magic
    @needs_local_scope
    def fh(line, local_ns):
        args = parse_argstring(fh, line)
        app = local_ns[args.app]
        return reloader.load(
            app, page=args.page, width=args.width, height=args.height, port=args.port
        )


# This implementation draws inspiration from Gradio.
# https://github.com/gradio-app/gradio/blob/main/gradio/ipython_ext.py
# https://github.com/gradio-app/gradio/blob/main/gradio/http_server.py
class Server(uvicorn.Server):
    def __init__(self, config: uvicorn.Config) -> None:
        self.running_app = config.app
        super().__init__(config)

    def install_signal_handlers(self):
        pass

    def run_in_thread(self):
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
        start = time.time()
        while not self.started:
            time.sleep(1e-3)
            if time.time() - start > 5:
                raise Exception("Server failed to start. Please check that the port is available.")

    def close(self):
        self.should_exit = True
        self.thread.join(timeout=5)


class JupyterReloader:
    def __init__(self) -> None:
        self.server: Server | None = None

    def load(
        self,
        app,
        page="/",
        width: str = "70%",
        height: str = "300",
        port: int | None = None,
        host: str = "0.0.0.0",
    ):
        server = self.server
        port = port or (server and server.config.port) or find_available_port(host)
        config = uvicorn.Config(app=app, port=port, host=host, log_level="warning")
        if server is not None:
            server.close()
        server = Server(config=config)
        server.run_in_thread()
        self.server = server
        local_url = f"http://{host}:{port}{page}"
        display(
            Pretty(f"App run at {local_url}"),
            IFrame(
                local_url,
                width=width,
                height=height,
                allow="autoplay; camera; microphone; clipboard-read; clipboard-write;",
                frameborder="0",
                extras=["allowfullscreen"],
            ),
        )
        return TupleNoPrint((port, local_url, server))


class TupleNoPrint(tuple):
    # To remove printing function return in notebook
    def __repr__(self):
        return ""

    def __str__(self):
        return ""


def find_available_port(host):
    for port in PORT_RANGE:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            if sock.connect_ex((host, port)) != 0:
                return port
    raise Exception(
        f"Cannot find empty port in range: {PORT_RANGE.start}-{PORT_RANGE.stop}. You can specify a different port by using -p argument"
    )
