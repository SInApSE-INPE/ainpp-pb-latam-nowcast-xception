from pathlib import Path

from xception_nowcast._runtime.deployment import render_units

if __name__ == "__main__":
    render_units(
        Path(__file__).resolve().parent.parent, "xception_nowcast", "Xception", "xception-now"
    )
