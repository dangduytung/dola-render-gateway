"""Signed cookie helpers for the Dola Studio web login."""
import base64
import hashlib
import hmac
import html
import time


def _signature(payload: str, secret: str) -> str:
    return hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def create_session_token(username: str, secret: str, now: int | None = None) -> str:
    issued_at = int(time.time() if now is None else now)
    payload = f"{username}:{issued_at}"
    encoded = base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")
    return f"{encoded}.{_signature(encoded, secret)}"


def verify_session_token(
    token: str | None,
    username: str,
    secret: str,
    now: int | None = None,
    max_age: int = 12 * 60 * 60,
) -> bool:
    if not token or not username or not secret or "." not in token:
        return False
    encoded, supplied_signature = token.rsplit(".", 1)
    if not hmac.compare_digest(_signature(encoded, secret), supplied_signature):
        return False
    try:
        padded = encoded + "=" * ((4 - len(encoded) % 4) % 4)
        payload = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        token_username, issued_at_raw = payload.rsplit(":", 1)
        issued_at = int(issued_at_raw)
    except (ValueError, UnicodeDecodeError):
        return False
    current = int(time.time() if now is None else now)
    return token_username == username and 0 <= current - issued_at <= max_age


def render_login_html(error: str = "") -> str:
    error_html = (
        f'<div class="err">{html.escape(error)}</div>' if error else ""
    )
    return LOGIN_HTML.replace("__ERROR__", error_html)


LOGIN_HTML = """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Đăng nhập — Dola Studio</title><style>
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;background:#f5f3ef;color:#1d1d1f;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}.card{width:min(92vw,390px);background:#fff;border:1px solid #dedbd4;border-radius:20px;padding:32px;box-shadow:0 18px 60px #2f2a2014}.mark{width:48px;height:48px;display:grid;place-items:center;border-radius:14px;background:#181817;color:#fff;font-size:24px}h1{font-size:25px;margin:20px 0 7px}.sub{color:#75716a;font-size:14px;margin:0 0 24px}.field{display:grid;gap:7px;margin:14px 0}.field span{font-size:12px;font-weight:650;color:#5f5b55}input{width:100%;border:1px solid #d7d3cb;border-radius:11px;padding:12px 13px;font-size:15px;outline:none}input:focus{border-color:#242321;box-shadow:0 0 0 3px #24232112}button{width:100%;border:0;border-radius:11px;padding:13px;background:#1e1e1c;color:#fff;font-weight:700;font-size:14px;cursor:pointer;margin-top:9px}.err{background:#fff0ee;color:#a42b1e;border:1px solid #f0c8c2;border-radius:9px;padding:10px 12px;font-size:13px;margin-bottom:14px}</style></head>
<body><main class="card"><div class="mark">◉</div><h1>Dola Studio</h1><p class="sub">Đăng nhập để vào bảng điều khiển render.</p>__ERROR__<form method="post" action="/login"><label class="field"><span>TÊN ĐĂNG NHẬP</span><input name="username" autocomplete="username" autofocus required></label><label class="field"><span>MẬT KHẨU</span><input type="password" name="password" autocomplete="current-password" required></label><button type="submit">Đăng nhập</button></form></main></body></html>"""
