import os
import sys
import traceback


LOG_PATH = os.path.abspath("flask_launcher.log")


def _log(message: str) -> None:
    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(message + "\n")
        log.flush()


def main() -> None:
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    sys.stdout = open(os.path.abspath("flask_launcher.out.log"), "a", encoding="utf-8", buffering=1)
    sys.stderr = open(os.path.abspath("flask_launcher.err.log"), "a", encoding="utf-8", buffering=1)

    try:
        _log("[run_flask] starting import")
        from app import app

        port = int(os.getenv("FLASK_PORT", "5000"))
        reload_enabled = os.getenv("APP_ENV", "development").lower() != "production"
        _log(f"[run_flask] serving on 127.0.0.1:{port} reload={reload_enabled}")
        app.run(host="127.0.0.1", port=port, debug=False, use_reloader=reload_enabled)
    except Exception:
        _log("[run_flask] fatal error")
        _log(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
