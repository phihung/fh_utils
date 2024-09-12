from unittest import mock

from fasthtml.common import to_xml
from fasthtml.svg import transformd
from inline_snapshot import snapshot

from fh_utils import heroicons


def test_HeroIcon(tmp_path):
    with mock.patch.object(heroicons, "DIR", tmp_path):
        exp1 = snapshot(
            '<svg viewbox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" stroke-width="1.5" stroke="currentColor" fill="none" class="size-10 fill-green-100 stroke-red-500 rotate-45">  <path stroke-linecap="round" stroke-linejoin="round" d="M7.5 14.25v2.25m3-4.5v4.5m3-6.75v6.75m3-9v9M6 20.25h12A2.25 2.25 0 0 0 20.25 18V6A2.25 2.25 0 0 0 18 3.75H6A2.25 2.25 0 0 0 3.75 6v12A2.25 2.25 0 0 0 6 20.25Z"/></svg>\n'
        )
        exp2 = snapshot(
            '<svg viewbox="0 0 20 20" xmlns="http://www.w3.org/2000/svg" fill="green" width="40" stroke="red" transform="rotate(45,25,25)">  <path fill-rule="evenodd" d="M4.25 2A2.25 2.25 0 0 0 2 4.25v11.5A2.25 2.25 0 0 0 4.25 18h11.5A2.25 2.25 0 0 0 18 15.75V4.25A2.25 2.25 0 0 0 15.75 2H4.25ZM15 5.75a.75.75 0 0 0-1.5 0v8.5a.75.75 0 0 0 1.5 0v-8.5Zm-8.5 6a.75.75 0 0 0-1.5 0v2.5a.75.75 0 0 0 1.5 0v-2.5ZM8.584 9a.75.75 0 0 1 .75.75v4.5a.75.75 0 0 1-1.5 0v-4.5a.75.75 0 0 1 .75-.75Zm3.58-1.25a.75.75 0 0 0-1.5 0v6.5a.75.75 0 0 0 1.5 0v-6.5Z" clip-rule="evenodd"/></svg>\n'
        )
        for _ in range(2):
            e1 = heroicons.Heroicon(
                "chart-bar-square", cls="size-10 fill-green-100 stroke-red-500 rotate-45"
            )
            assert to_xml(e1) == exp1

            e2 = heroicons.Heroicon(
                "chart-bar-square",
                "20/solid",
                width=40,
                stroke="red",
                fill="green",
                **transformd(rotate=(45, 25, 25)),
            )

            assert to_xml(e2) == exp2
