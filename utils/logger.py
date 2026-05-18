import json
import datetime
import traceback
import logging
import config

log = logging.getLogger("docgen")


def clear_logs():
    for f in (config.JSON_LOG_FILE, config.ERROR_LOG_FILE):
        try:
            f.write_text("")
        except Exception:
            pass


def log_event(agent: str, event: str, details: dict | None = None):
    if details:
        token_info = f" | in={details.get('input_tokens', '')} out={details.get('output_tokens', '')} total={details.get('total_tokens', '')}"
        log.info(f"[{agent}] {event}{token_info}")
    else:
        log.info(f"[{agent}] {event}")

    if not config.ENABLE_LOGGING:
        return
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "agent": agent,
        "event": event,
        "details": details or {},
    }
    try:
        with open(config.JSON_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
    except Exception:
        pass


def log_error(exc: Exception, context: str = ""):
    log.error(f"[{context}] {type(exc).__name__}: {exc}")
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "context": context,
        "type": type(exc).__name__,
        "message": str(exc),
        "traceback": traceback.format_exc(),
    }
    try:
        with open(config.ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass
