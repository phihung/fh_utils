import re
from typing import Literal

from diskcache import Cache
from fastcore.meta import delegates
from fastcore.net import urlread
from fasthtml.common import NotStr, ft_hx
from fasthtml.svg import ft_svg

from fh_utils.constants import CACHE_DIR

cache = Cache(CACHE_DIR / "icons")


@cache.memoize(tag="hero")
def _get_heroicon(name, variant):
    url = f"https://raw.githubusercontent.com/tailwindlabs/heroicons/master/optimized/{variant}/{name}.svg"
    return _parse(urlread(url))


_heroicon_defaults = {
    "outline": dict(stroke_width="1.5", stroke="currentColor", fill="none"),
    "solid": dict(fill="currentColor"),
}


@delegates(ft_svg)
def HeroIcon(
    name: str,
    variant: Literal["24/outline", "24/solid", "20/solid", "16/solid"] = "24/outline",
    **kwargs,
):
    """Svg Icon from heroicons.com"""
    kwargs = {**_heroicon_defaults[variant[3:]], **kwargs}
    return _make(_get_heroicon(name, variant), kwargs)


@cache.memoize(tag="ph")
def _get_phosphor_icon(name, variant):
    fn = name if variant == "regular" else f"{name}-{variant}"
    url = f"https://raw.githubusercontent.com/phosphor-icons/core/main/assets/{variant}/{fn}.svg"
    return _parse(urlread(url))


@delegates(ft_svg)
def PhIcon(
    name: str,
    variant: Literal["thin", "light", "regular", "bold", "fill", "duotone"] = "light",
    **kwargs,
):
    """Svg Icon from phosphoricons.com"""
    return _make(_get_phosphor_icon(name, variant), kwargs)


@cache.memoize(tag="ion")
def _get_ionicon(name, variant):
    variant = "" if not variant else "-" + variant
    url = f"https://raw.githubusercontent.com/ionic-team/ionicons/main/src/svg/{name}{variant}.svg"
    return _parse(urlread(url))


@delegates(ft_svg)
def IonIcon(
    name: str,
    variant: Literal["", "sharp", "outline"] = "",
    **kwargs,
):
    """Svg Icon from ionic.io"""
    return _make(_get_ionicon(name, variant), kwargs)


@cache.memoize(tag="lc")
def _get_lucide(name, variant):
    url = f"https://raw.githubusercontent.com/lucide-icons/lucide/main/icons/{name}.svg"
    return _parse(urlread(url))


@delegates(ft_svg)
def LcIcon(name: str, variant: Literal[""] = "", **kwargs):
    """Svg Icon from lucide.dev"""
    return _make(_get_lucide(name, variant), kwargs)


@cache.memoize(tag="fa")
def _get_fa(name, variant):
    url = f"https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/{variant}/{name}.svg"  # fmt: skip
    return _parse(urlread(url))


@delegates(ft_svg)
def FaIcon(name: str, variant: Literal["regular", "solid", "brands"] = "regular", **kwargs):
    """Svg Icon from fontawesome.com"""
    return _make(_get_fa(name, variant), kwargs)


@cache.memoize(tag="bs")
def _get_boostrap(name, variant):
    url = f"https://raw.githubusercontent.com/twbs/icons/main/icons/{name}.svg"  # fmt: skip
    return _parse(urlread(url))


@delegates(ft_svg)
def BsIcon(name: str, variant: Literal[""] = "", **kwargs):
    """Svg Icon from getbootstrap.com"""
    return _make(_get_boostrap(name, variant), kwargs)


@cache.memoize(tag="box")
def _get_boxicon(name, variant):
    p = "" if variant == "regular" else variant[0]
    url = f"https://raw.githubusercontent.com/atisawd/boxicons/master/svg/{variant}/bx{p}-{name}.svg"  # fmt: skip
    return _parse(urlread(url))


@delegates(ft_svg)
def BoxIcon(name: str, variant: Literal["regular", "solid", "logos"] = "regular", **kwargs):
    """Svg Icon from boxicons.com"""
    return _make(_get_boxicon(name, variant), kwargs)


xmlns = "http://www.w3.org/2000/svg"
pat = re.compile('<[^>]+viewBox="0 0 (\d+) (\d+)"[^>]*>(.*)</svg>')


def _parse(svg):
    """Return w, h and children"""
    svg = svg.replace("\n", "")
    return pat.match(svg).groups()


def _make(args, kwargs):
    w, h, content = args
    kwargs = {"viewBox": f"0 0 {w} {h}", "xmlns": xmlns, **kwargs}
    return ft_hx("svg", NotStr(content), **kwargs)
