from fasthtml.common import Button, Div, fast_app, serve

from fh_utils.tailwind import add_daisy_and_tailwind

app, rt = fast_app(static_path="public", pico=False)
add_daisy_and_tailwind(app)


@app.get("/")
def index():
    return Div(
        Button("Primary", cls="btn btn-primary"),
        Button("Secondary", cls="btn btn-secondary"),
        Button("Accent", cls="btn btn-accent"),
        data_theme="cupcake",
        cls="p-4",
    )


def main():
    serve(f"{__package__}.demo", "app")


if __name__ == "__main__":
    main()
