import time

from fasthtml.common import H2, fast_app

from fh_utils import no_reload_cache, serve

app, rt = fast_app()


@app.get("/")
def home():
    model = load_model()
    return H2(model("TRY TO MODIFY THIS TEXT AND SAVE. load_model should NOT be reexecuted"))


@no_reload_cache
def load_model():
    print("MODEL RELOAD: This message should be print only ONCE")
    time.sleep(1)
    return lambda x: x.upper()


if __name__ == "__main__":
    # Run with: python examples/demo2.py
    # Or with : fh_utils dev examples/demo2.py
    serve()
