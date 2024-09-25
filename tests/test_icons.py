from unittest import mock

import pytest
from diskcache import ENOVAL
from fasthtml.common import to_xml
from fasthtml.svg import transformd
from inline_snapshot import snapshot

from fh_utils import icons


@pytest.mark.parametrize("cls,name,vars", [
    (icons.IonIcon, "boat", ("", "sharp", "outline")),
    (icons.HeroIcon, "chart-bar-square", ("24/outline", "24/solid", "20/solid", "16/solid")),
    (icons.PhIcon, "airplane-in-flight", ("thin", "light", "regular", "bold", "fill", "duotone")),
    (icons.LcIcon, "message-square-heart", ("",)),
    (icons.FaIcon, "bell", ("regular", "solid")),
    (icons.FaIcon, "apple", ("brands",)),
    (icons.BsIcon, "apple", ("",)),
    (icons.BoxIcon, "apple", ("logos",)),
    (icons.BoxIcon, "smile", ("regular", "solid")),
])  # fmt: skip
def test_icons(cls, name, vars):
    def run_test():
        for v in vars:
            e = cls(name, v, width=20)
            assert e.width == 20

    run_test()
    with mock.patch.object(icons.cache, "get", return_value=ENOVAL):
        run_test()


def test_HeroIcon(tmp_path):
    exp1 = snapshot(
        '<svgviewbox="002424"xmlns="http://www.w3.org/2000/svg"stroke-width="1.5"stroke="currentColor"fill="none"class="size-10fill-green-100stroke-red-500rotate-45"><pathstroke-linecap="round"stroke-linejoin="round"d="M7.514.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M620.25h12A2.252.2500020.2518V6A2.252.25000183.75H6A2.252.250003.756v12A2.252.25000620.25Z"/></svg>'
    )
    exp2 = snapshot(
        '<svg viewbox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" fill="green" width="40" stroke="red" transform="rotate(45,25,25)">  <path fill-rule="evenodd" d="M4.25 2A2.25 2.25 0 0 0 2 4.25v11.5A2.25 2.25 0 0 0 4.25 18h11.5A2.25 2.25 0 0 0 18 15.75V4.25A2.25 2.25 0 0 0 15.75 2H4.25ZM15 5.75a.75.75 0 0 0-1.5 0v8.5a.75.75 0 0 0 1.5 0v-8.5Zm-8.5 6a.75.75 0 0 0-1.5 0v2.5a.75.75 0 0 0 1.5 0v-2.5ZM8.584 9a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5a.75.75 0 0 1 .75-.75Zm3.58-1.25a.75.75 0 0 0-1.5 0v6.5a.75.75 0 0 0 1.5 0v-6.5Z" clip-rule="evenodd"/></svg>'
    )

    def run_test():
        e1 = icons.HeroIcon(
            "chart-bar-square", cls="size-10 fill-green-100 stroke-red-500 rotate-45"
        )
        assert to_xml(e1).replace(" ", "") == exp1

        e2 = icons.HeroIcon(
            "chart-bar-square",
            "20/solid",
            width=40,
            stroke="red",
            fill="green",
            **transformd(rotate=(45, 25, 25)),
        )

        assert to_xml(e2) == exp2

    run_test()
    with mock.patch.object(icons.cache, "get", return_value=ENOVAL):
        run_test()
