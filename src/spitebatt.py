#!/usr/bin/env python3
import subprocess
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

HELPER = "/usr/local/lib/mint-battery-toggle/apply-profile"

def run_profile(profile: str, status: Gtk.Label):
    try:
        # One GUI prompt via pkexec
        subprocess.run(["pkexec", HELPER, profile], check=True)
        status.set_text(f"{profile} applied successfully ✅")
    except subprocess.CalledProcessError as e:
        status.set_text(f"Failed ❌ (exit {e.returncode})")
    except FileNotFoundError:
        status.set_text(f"Missing helper: {HELPER}")

class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="io.github.spitelon.spitebatt")

    def do_activate(self):
        win = Gtk.ApplicationWindow(application=self)
        win.set_title("SpiteBatt")
        win.set_default_size(420, 220)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        for m in ("top","bottom","start","end"):
            getattr(box, f"set_margin_{m}")(16)

        title = Gtk.Label(label="Battery charging profiles")
        title.set_xalign(0)

        status = Gtk.Label(label="Ready")
        status.set_xalign(0)

        btn_home = Gtk.Button(label="Home (40–80%)")
        btn_travel = Gtk.Button(label="On-the-go (0–100%)")

        btn_home.connect("clicked", lambda _b: run_profile("home", status))
        btn_travel.connect("clicked", lambda _b: run_profile("travel", status))

        box.append(title)
        box.append(status)
        box.append(btn_home)
        box.append(btn_travel)

        win.set_child(box)
        win.present()

if __name__ == "__main__":
    App().run()
