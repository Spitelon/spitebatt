#!/usr/bin/env python3
import subprocess
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib


# ---------- Config ----------
APP_ID = "io.github.spitelon.spitebatt"
HELPER = "/usr/local/lib/mint-battery-toggle/apply-profile"
ACTIVE_FILE = Path("/var/lib/mint-battery-toggle/active_profile")
DEFAULT_STATUS = "Select a profile to apply."


# ---------- Helpers ----------
def set_status(label: Gtk.Label, text: str, kind: str = "info") -> None:
    label.set_text(text)

    ctx = label.get_style_context()
    ctx.remove_class("error")
    ctx.remove_class("warning")
    ctx.remove_class("success")

    if kind in ("error", "warning", "success"):
        ctx.add_class(kind)


def reset_status_later(label: Gtk.Label, seconds: int = 4) -> None:
    GLib.timeout_add_seconds(
        seconds,
        lambda: (set_status(label, DEFAULT_STATUS), False)[1],
    )


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


# ---------- UI ----------
class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)

    def do_activate(self):
        win = Gtk.ApplicationWindow(application=self)
        win.set_title("SpiteBatt")
        win.set_default_size(460, 320)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer.set_hexpand(True)
        outer.set_vexpand(True)
        outer.set_valign(Gtk.Align.CENTER)
        outer.set_halign(Gtk.Align.CENTER)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        content.set_margin_top(20)
        content.set_margin_bottom(20)
        content.set_margin_start(20)
        content.set_margin_end(20)
        content.set_size_request(360, -1)

        title = Gtk.Label(label="SpiteBatt")
        title.set_xalign(0.5)
        title.get_style_context().add_class("title-1")

        subtitle = Gtk.Label(label="Choose how your battery should behave")
        subtitle.set_xalign(0.5)
        subtitle.set_wrap(True)
        subtitle.set_justify(Gtk.Justification.CENTER)

        active_label = Gtk.Label(label="Active profile: Not set yet")
        active_label.set_xalign(0.5)

        status = Gtk.Label(label=DEFAULT_STATUS)
        status.set_xalign(0.5)
        status.set_wrap(True)
        status.set_justify(Gtk.Justification.CENTER)

        btn_home = Gtk.Button(label="Home")
        btn_home.set_size_request(320, -1)

        lbl_home = Gtk.Label(label="Optimized for long battery health when plugged in")
        lbl_home.set_xalign(0.5)
        lbl_home.set_wrap(True)
        lbl_home.set_justify(Gtk.Justification.CENTER)

        btn_travel = Gtk.Button(label="On-the-go")
        btn_travel.set_size_request(320, -1)

        lbl_travel = Gtk.Label(label="Full charge for travel and long days away")
        lbl_travel.set_xalign(0.5)
        lbl_travel.set_wrap(True)
        lbl_travel.set_justify(Gtk.Justification.CENTER)

        def apply_active_ui() -> bool:
            active = read_active_profile()

            btn_home.get_style_context().remove_class("suggested-action")
            btn_travel.get_style_context().remove_class("suggested-action")

            if active == "home":
                active_label.set_text("Active profile: Home (40–80%)")
                btn_home.get_style_context().add_class("suggested-action")
            elif active == "travel":
                active_label.set_text("Active profile: On-the-go (0–100%)")
                btn_travel.get_style_context().add_class("suggested-action")
            else:
                active_label.set_text("Active profile: Not set yet")

            return True

        def on_home(_b):
            run_profile("home", status)
            apply_active_ui()

        def on_travel(_b):
            run_profile("travel", status)
            apply_active_ui()

        btn_home.connect("clicked", on_home)
        btn_travel.connect("clicked", on_travel)

        content.append(title)
        content.append(subtitle)
        content.append(active_label)
        content.append(btn_home)
        content.append(lbl_home)
        content.append(btn_travel)
        content.append(lbl_travel)
        content.append(status)

        outer.append(content)
        win.set_child(outer)
        win.present()

        apply_active_ui()
        GLib.timeout_add_seconds(2, apply_active_ui)


if __name__ == "__main__":
    App().run()
