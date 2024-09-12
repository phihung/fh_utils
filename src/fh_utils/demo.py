from fasthtml.common import Button, Div, fast_app, serve
from fasthtml.svg import transformd

from fh_utils.heroicons import Heroicon
from fh_utils.tailwind import add_daisy_and_tailwind

app, rt = fast_app(static_path="public", pico=False)
add_daisy_and_tailwind(app)


@app.get("/")
def index():
    return Div(heroicons_bar(), daisy_bar(), cls="mt-10")


def daisy_bar():
    return Div(
        Button("Primary", cls="btn btn-primary"),
        Button("Secondary", cls="btn btn-secondary"),
        Button("Accent", cls="btn btn-accent"),
        data_theme="cupcake",
        cls="p-4 flex gap-4",
    )


def heroicons_bar():
    return Div(
        Heroicon("chart-bar-square", cls="size-10 fill-green-100 stroke-red-500 rotate-45"),
        Heroicon(
            "chart-bar-square",
            "20/solid",
            width=40,
            stroke="red",
            fill="green",
            **transformd(rotate=(45, 25, 25)),
        ),
        cls="p-4 flex gap-4",
    )


def main():
    serve(f"{__package__}.demo", "app")


if __name__ == "__main__":
    main()
