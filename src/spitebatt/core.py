import subprocess
from gi.repository import Gtk, GLib

from .config import HELPER, ACTIVE_FILE, DEFAULT_STATUS


def set_status(label: Gtk.Label, text: str, kind: str = "info") -> None:
    label.set_text(text)

    ctx = label.get_style_context()
    ctx.remove_class("status-success")
    ctx.remove_class("status-error")
    ctx.remove_class("status-warning")

    if kind == "success":
        ctx.add_class("status-success")
    elif kind == "error":
        ctx.add_class("status-error")
    elif kind == "warning":
        ctx.add_class("status-warning")


def reset_status_later(label: Gtk.Label, seconds: int = 4) -> None:
    GLib.timeout_add_seconds(seconds, lambda: (set_status(label, DEFAULT_STATUS), False)[1])


def read_active_profile() -> str | None:
    try:
        v = ACTIVE_FILE.read_text().strip().lower()
        return v if v in ("home", "travel") else None
    except Exception:
        return None


def run_profile(profile: str, status: Gtk.Label) -> None:
    try:
        subprocess.run(
            ["pkexec", HELPER, profile],
            check=True,
            text=True,
            capture_output=True,
        )
        set_status(status, f"✅ {profile.capitalize()} applied successfully.", "success")
        reset_status_later(status, 4)

    except subprocess.CalledProcessError as e:
        code = e.returncode
        err = (e.stderr or "").lower()

        if code == 126:
            if "cancel" in err:
                set_status(status, "Cancelled. No changes were made.", "warning")
            elif "authentication failed" in err or "failed" in err:
                set_status(status, "Authentication failed. Please try again.", "error")
            else:
                set_status(status, "Authentication was not completed.", "warning")

        elif code == 127:
            set_status(status, "Error: pkexec is missing. Install 'policykit-1'.", "error")
        else:
            set_status(status, "Error applying profile. Please try again.", "error")
            print(f"[SpiteBatt] cmd: {e.cmd} (exit {code})")
            print(f"[SpiteBatt] stderr: {e.stderr}")
            print(f"[SpiteBatt] stdout: {e.stdout}")

    except FileNotFoundError:
        set_status(status, "Installation error: helper script not found.", "error")
        print(f"[SpiteBatt] Missing helper: {HELPER}")
