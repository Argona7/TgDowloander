from pathlib import Path
import os

def load_dotenv(paths=None, override=True):
    if paths is None:
        here = Path(__file__).resolve().parent.parent
        paths = [here / ".env", Path.cwd() / ".env", here / ".env.local", Path.cwd() / ".env.local"]

    def parse_line(line: str):
        line = line.lstrip("\ufeff").strip()
        if not line or line.startswith("#") or "=" not in line:
            return None, None
        k, v = line.split("=", 1)
        k = k.strip()
        v_raw = v.strip()
        if (v_raw.startswith('"') and v_raw.endswith('"')) or (v_raw.startswith("'") and v_raw.endswith("'")):
            v = v_raw[1:-1]
        else:
            v = v_raw.split("#", 1)[0].rstrip()
        return k, v

    loaded = {}
    for p in paths:
        p = Path(p)
        if not p.exists():
            continue
        for raw in p.read_text(encoding="utf-8").splitlines():
            k, v = parse_line(raw)
            if not k:
                continue
            if override or (k not in os.environ):
                os.environ[k] = v
                loaded[k] = v
    return loaded

def env_int(name: str, default=None):
    v = os.environ.get(name)
    if v is None or v == "":
        return default
    try:
        return int(v)
    except ValueError:
        return default

def mask(s: str, keep: int = 4) -> str:
    if not s:
        return ""
    return s[:keep] + "…" if len(s) > keep else "…"