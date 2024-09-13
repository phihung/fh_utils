from fasthtml.common import Button, Div, fast_app, serve

from fh_utils.icons import BoxIcon, BsIcon, FaIcon, HeroIcon, IonIcon, LcIcon, PhIcon
from fh_utils.tailwind import add_daisy_and_tailwind

app, rt = fast_app(static_path="public", pico=False)
add_daisy_and_tailwind(app)


@app.get("/")
def index():
    return Div(cls="mt-10", data_theme="cupcake")(
        icons_bar(),
        daisy_bar(),
    )


def daisy_bar():
    return Div(cls="p-4 flex gap-4")(
        Button("Primary", cls="btn btn-primary"),
        Button("Secondary", cls="btn btn-secondary"),
        Button("Accent", cls="btn btn-accent"),
    )


def icons_bar():
    kw1 = dict(cls="size-10 fill-green-100 stroke-red-500 rotate-45")
    kw2 = dict(width=40, stroke="red")
    return Div(cls="p-4 flex gap-4")(
        HeroIcon("chart-bar-square", **kw1),
        HeroIcon("chart-bar-square", **kw2),
        PhIcon("airplane-in-flight", **kw1),
        PhIcon("airplane-in-flight", "fill", **kw2),
        IonIcon("boat", **kw1),
        IonIcon("boat", "sharp", **kw2),
        LcIcon("message-square-heart", **kw1),
        LcIcon("message-square-heart", **kw2),
        FaIcon("bell", **kw1),
        FaIcon("apple", "brands", **kw2),
        BsIcon("bell", **kw1),
        BsIcon("apple", "", **kw2),
        BoxIcon("signal-5", "regular", **kw1),
        BoxIcon("discord", "logos", **kw2),
    )


def main():
    serve(f"{__package__}.demo", "app")


if __name__ == "__main__":
    main()
