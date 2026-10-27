import json, logging
DEFAULTS = {"bots": ["streamelements", "nightbot", "moobot", "fossabot"]}

log = logging.getLogger(__name__)

def load_config(path: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
            config = {**DEFAULTS, **loaded}
            config["bots"] = set(DEFAULTS["bots"]) | set(loaded.get("extra_bots", []))
            return config
    except FileNotFoundError:
        log.error("Config file not found.")
    except json.decoder.JSONDecodeError:
        log.error("Config file could not be json decoded.")

    return DEFAULTS