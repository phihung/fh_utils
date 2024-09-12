# fh_utils

A collection of utilities for FastHTML projects.

If you don’t like to _pip install_, feel free to copy and paste the code! The project is structured to make copying and pasting easy.

## Docs

Installation

```bash
pip install fh_utils
uv add fh_utils
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
uv run demo
rm -rf dist && uv build
uvx twine upload dist/*
```
