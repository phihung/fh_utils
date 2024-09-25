import logging
import os
import platform
import stat
import subprocess
import tempfile
from pathlib import Path

from fastcore.net import urlsave
from fasthtml.common import FastHTML, FileResponse, Link

from fh_utils.constants import CACHE_DIR

TAILWIND_URI = "/fh-utils/tailwindcss"

# tailwind.config.js file
TAILWIND_CONFIG = """
/** @type {import('tailwindcss').Config} */

const plugin = require("tailwindcss/plugin");

module.exports = {
  content: ["**/*.py"],
  theme: {
    extend: {},
  },
  plugins: [
    require("@tailwindcss/typography"),
    // daisy
    plugin(function ({ addVariant }) {
      addVariant("htmx-settling", ["&.htmx-settling", ".htmx-settling &"]);
      addVariant("htmx-request", ["&.htmx-request", ".htmx-request &"]);
      addVariant("htmx-swapping", ["&.htmx-swapping", ".htmx-swapping &"]);
      addVariant("htmx-added", ["&.htmx-added", ".htmx-added &"]);
    }),
  ],
};
"""

TAILWIND_DAISYCSS_CONFIG = TAILWIND_CONFIG.replace("// daisy", 'require("daisyui"),')

TAILWIND_SOURCE_CSS = """
@tailwind base;
@tailwind components;
@tailwind utilities;
"""


def add_tailwind(
    app: FastHTML,
    cfg: str = TAILWIND_CONFIG,
    css: str = TAILWIND_SOURCE_CSS,
    uri: str = TAILWIND_URI,
):
    return _add(app, cfg, css, uri)


def add_daisy_and_tailwind(
    app: FastHTML,
    cfg: str = TAILWIND_DAISYCSS_CONFIG,
    css: str = TAILWIND_SOURCE_CSS,
    uri: str = TAILWIND_URI,
):
    return _add(app, cfg, css, uri)


def _add(app: FastHTML, cfg, css, uri):
    outcss = tempfile.NamedTemporaryFile(delete=False)
    app.router.on_startup.append(lambda: tailwind_compile(Path(outcss.name), cfg, css))
    app.hdrs.append(Link(rel="stylesheet", href=uri))

    @app.get(uri)
    def _():
        return FileResponse(outcss.name, filename="app.css")

    logging.info(f"Tailwind is served at {uri}")
    return app


def tailwind_compile(
    outpath: str | Path, cfg: str = TAILWIND_CONFIG, css: str = TAILWIND_SOURCE_CSS
):
    outpath = Path(outpath)
    outpath.parent.mkdir(exist_ok=True, parents=True)

    kwargs = {
        "cwd": os.getcwd(),
        "env": {},
        "capture_output": False,
        "check": False,
    }

    cfg_path = Path(tempfile.NamedTemporaryFile().name)
    css_path = Path(tempfile.NamedTemporaryFile().name)

    cfg_path.write_text(cfg)
    css_path.write_text(css)

    cli = _cached_download_tailwind_cli()
    subprocess.run([str(cli), "-c", cfg_path, "-i", css_path, "-o", outpath], **kwargs)


def _cached_download_tailwind_cli(version="latest") -> Path:
    ext = ".exe" if platform.system().lower() == "win32" else ""
    path = CACHE_DIR / f"tailwindcss{ext}"
    if path.exists():
        return path
    url = _get_download_url(version)
    urlsave(url, path)
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


def _get_download_url(version):
    os_name, arch = platform.system().lower(), platform.machine().lower()
    os_name = os_name.lower().replace("win32", "windows").replace("darwin", "macos")
    ext = ".exe" if os_name == "windows" else ""

    target = {
        "amd64": f"{os_name}-x64{ext}",
        "x86_64": f"{os_name}-x64{ext}",
        "arm64": f"{os_name}-arm64",
        "aarch64": f"{os_name}-arm64",
    }[arch.lower()]

    v = "download" if version == "latest" else version
    return (
        f"https://github.com/dobicinaitis/tailwind-cli-extra/releases/latest/{v}/tailwindcss-extra-{target}"
        # f"https://github.com/tailwindlabs/tailwindcss/releases/latest/{v}/tailwindcss-{target}"
    )
