import os
from pathlib import Path

ROOT = Path(__file__).parent.parent

STORE_PATH = Path(os.environ["LINKEDWITH_STORE"]) if "LINKEDWITH_STORE" in os.environ else ROOT / "data" / "linkedwith.json"
CONTACT_INFO_PATH = Path(os.environ["LINKEDWITH_CONTACT_INFO"]) if "LINKEDWITH_CONTACT_INFO" in os.environ else ROOT / "data" / "contact_info.csv"
HTML_OUTPUT_PATH = Path(os.environ["LINKEDWITH_HTML_OUTPUT"]) if "LINKEDWITH_HTML_OUTPUT" in os.environ else ROOT / "output" / "LinkedWith.HTML"
