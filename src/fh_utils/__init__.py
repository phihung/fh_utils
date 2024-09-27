from importlib.metadata import version

from fh_utils.icons import BoxIcon, FaIcon, HeroIcon, IonIcon, LcIcon, PhIcon  # noqa: F401
from fh_utils.ipython_ext import load_ipython_extension  # noqa: F401
from fh_utils.server import no_reload, no_reload_cache, serve  # noqa: F401
from fh_utils.tailwind import add_daisy_and_tailwind, add_tailwind, tailwind_compile  # noqa: F401

__version__ = version("fh_utils")
