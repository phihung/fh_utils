from functools import cache
from typing import Literal

from fastcore.net import urlread
from fasthtml.common import NotStr, ft_hx

from fh_utils.constants import CACHE_DIR

DIR = CACHE_DIR / "heroicons"
DIR.mkdir(exist_ok=True, parents=True)

defaults = {
    "outline": dict(stroke_width="1.5", stroke="currentColor", fill="none"),
    "solid": dict(fill="currentColor"),
}


def Heroicon(
    name: str,
    variant: Literal["24/outline", "24/solid", "20/solid", "16/solid"] = "24/outline",
    **kwargs,
):
    size, type = variant.split("/", 1)
    content = cached_download(name, variant)
    kwargs = {
        "viewBox": f"0 0 {size} {size}",
        "xmlns": "http://www.w3.org/2000/svg",
        **defaults[type],
        **kwargs,
    }
    return ft_hx("svg", NotStr(content), **kwargs)


@cache
def cached_download(name, variant):
    fn = DIR / f"optimized_{variant.replace('/', '_')}_{name}.txt"
    if not fn.exists():
        url = f"https://raw.githubusercontent.com/tailwindlabs/heroicons/master/optimized/{variant}/{name}.svg"
        content = "".join(urlread(url).splitlines()[1:-1])
        fn.write_text(content)
        return content
    return fn.read_text()
