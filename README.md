# fh_utils

A collection of utilities for FastHTML projects

**Features**

- CLI and **Fast** reload.
- Jupyter notebook extension to run FastHTML apps.
- Add Tailwind CSS / DaisyUI to your app without any boilerplate.
- Icon packs: Heroicons, Ionicons, Phosphor, Lucide, FontAwesome, Bootstrap, Boxicons.

Installation

```bash
pip install fh_utils
uv add fh_utils
```

If you don’t like to _pip install_, feel free to copy and paste the code! The project is structured to make copying and pasting easy.

## Docs

### Fast Reload

Automatically watch for changes and reload only the modified Python modules.

```bash
fh_utils dev path/to/your/app.py
fh_utils dev path/to/your/app.py --live  # with live update
```

You can also use `from fh_utils import serve` as a drop-in replacement for fasthtml's serve.

See [CLI section](#cli) for more information.

**Real-World Example**

In the following example, modifying `app.py` triggers fast-reload in under one second, while a full reload (i.e., Uvicorn reload) takes over 30 seconds.

```python
# app.py
from models import load_model
@app.post("/predict")
def home(text: str):
    # Modification in the file will not reload the other files
    emb = load_model().encode(text)
    return Div(f"Embedding shape: {emb.shape}", cls="text-pretty")

# models.py
from functools import cache
@cache
def load_model():
    # Importing takes 20 seconds; loading the model takes 15 seconds.
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("clip-ViT-B-32-multilingual-v1")
```

#### Caveats and Utilities

- We utilize IPython's **autoreload** magic under the hood, which comes with the same [caveats](https://ipython.readthedocs.io/en/stable/config/extensions/autoreload.html#caveats). This behavior may change in future releases.

- Fast reload works at the module level (i.e., per `.py` file). If a file is modified, the entire module is reloaded. In the previous example, if `load_model` is in the same `app.py` file, the cache will not persist, as the function is redefined with an empty cache during the `app` module reload.

To mitigate this, we provide the `no_reload_cache` and `no_reload` decorators, which prevent function redefinition during module reload. These decorators have **no impact** when fast reload is not used.

```python
from fh_utils import no_reload_cache

@no_reload_cache
def load_model():
    # The cache remains valid after a module fast-reload!
    # With `no_reload_cache`, it's safe to keep load_model in app.py
```

See [demo2](./examples/demo2.py) for a hands-on example.

### CLI

The CLI utility provides an improved way to start the FastHTML app.
It ensures consistency between development and production environments, eliminating the need to hardcode options like `live=True` or `reload=True` in the code.

```bash
fh_utils --help

# Start the app with "fast reload" and "live" updates
fh_utils dev src/app.py --live

# The command accepts Uvicorn arguments such as `--reload-include` and `--log-level` (refer to `uvicorn --help` for more details)
fh_utils dev src/app.py --port 8000 --log-level error --reload-include src

# Run with full Uvicorn reload
fh_utils dev src/app.py --reload full

# Production run: no reload, no live updates
fh_utils run src/app.py
```

### Jupyter Extension

One line magic to serve your `app` and displaying in the notebook

```python
from fasthtml.common import Title, Main, H1, P, Button, fast_app
app, rt = fast_app()
count = 0

@rt("/")
def home():
    return Title("Count Demo"), Main(
        H1("Count Demo"),
        P(f"Count is set to {count}", id="count"),
        Button("Increment", hx_post="/increment", hx_target="#count", hx_swap="innerHTML"),
    )
@rt
def increment():
    global count
    count += 1
    return f"Count is set to {count}"

%load_ext fh_utils
%fh app
```

The line magic can be used multiple time in the notebook

```python
print("Current count is", count)  # new value
count = 1234
%fh app
```

Full syntax

```bash
%fh?
%fh app [--page PAGE] [-w WIDTH] [-h HEIGHT] [-p PORT] app
```

### Tailwindcss and Daisycss

Add Tailwind/Daisy to your app without any boilerplate

```python
from fh_utils.tailwind import add_daisy_and_tailwind, add_tailwind, tailwind_compile

app, rt = fast_app(pico=False, static_path="public")

# Usage 1: Add Tailwind CSS
# The output css is saved as temporary file and served at /fh-utils/tailwindcss
add_tailwind(app)

# Usage 2: Add DaisyUI along with Tailwind CSS
add_daisy_and_tailwind(app)

# Usage 3: Customize Tailwind configuration
add_tailwind(app, cfg=Path("tailwind.config.js").read_text(), css="your custom css")

# Usage 4: Serve via FastHTML's static route
# Note: Don't forget to add public/app.css to your .gitignore
tailwind_compile("public/app.css")
app, rt = fast_app(hdrs=[Link(rel="stylesheet", href="app.css")], pico=False, static_path="public")
```

The Tailwind CLI is automatically downloaded, and your CSS files are compiled, served, and integrated into your app.

> [!NOTE]  
> Under the hood, we use the bundle provided by [dobicinaitis/tailwind-cli-extra](https://github.com/dobicinaitis/tailwind-cli-extra). Please consider giving the author a star for recognition.

#### Bonus: Using Tailwind CSS IntelliSense in VSCode

1. Install the [Tailwind CSS IntelliSense extension](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss)

2. Create a `tailwind.config.js` file at the root of your project and ensure that \*_/_.py is included in the content paths:

```js
module.exports = {
  content: ["**/*.py"],
};
```

See [here](src/fh_utils/tailwind.py) for a full example of config

3. Add the following settings to your .vscode/settings.json file to enable IntelliSense support for Tailwind classes in Python:

```json
{
  "tailwindCSS.classAttributes": ["class", "cls"],
  "tailwindCSS.includeLanguages": {
    "python": "html"
  }
}
```

### Icons

The icons are downloaded from github and saved in cache.

https://phosphoricons.com - MIT  
https://heroicons.com - MIT  
https://ionic.io/ionicons - MIT  
https://lucide.dev - Lucide License  
https://fontawesome.com - CC BY 4.0  
https://icons.getbootstrap.com - MIT
https://boxicons.com - MIT

```python
from fh_utils.icons import HeroIcon, IonIcon, LcIcon, PhIcon, FaIcon, BsIcon, BoxIcon

# Works nicely with tailwind
kw = dict(cls="size-10 fill-green-100 stroke-red-500 rotate-45")
PhIcon("airplane-in-flight", **kw)
Heroicon("chart-bar-square", **kw)
IonIcon("boat", **kw)
LcIcon("message-square-heart", **kw)
FaIcon("bell", **kw)
BsIcon("bell", **kw)
BoxIcon("smile", **kw)

# And without tailwind
kw = dict(width=40, stroke="red", fill="green")
PhIcon("airplane-in-flight", "fill", **kw)
Heroicon("chart-bar-square", "20/solid", **kw)
IonIcon("boat", "sharp", **kw)
LcIcon("message-square-heart", **kw)
FaIcon("apple", "brands", **kw)
BsIcon("apple", **kw)
BoxIcon("smile", **kw)
```

## Dev

```bash
uv sync
uv run pytest
uv run examples/demo.py
rm -rf dist && uv build
uvx twine upload dist/*
```
