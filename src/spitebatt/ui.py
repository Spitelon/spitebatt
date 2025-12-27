import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib

from .config import APP_ID, DEFAULT_STATUS
from .core import run_profile, read_active_profile


def load_css():
    css = b"""
    .status-success { color: #2ecc71; font-weight: 600; }
    .status-error   { color: #e74c3c; font-weight: 600; }
    .status-warning { color: #f39c12; font-weight: 600; }
    """
    provider = Gtk.CssProvider()
    provider.load_from_data(css)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
    )


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)

    def do_activate(self):
        load_css()

        # Config knobs for layout
        COL_WIDTH = 200
        BTN_WIDTH = 200
        WRAP_CHARS = 25
        PROFILES_GAP = 44

        win = Gtk.ApplicationWindow(application=self)
        win.set_title("SpiteBatt")
        win.set_default_size(520, 320)

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
        content.set_size_request(420, -1)
        content.set_hexpand(False)
        content.set_halign(Gtk.Align.CENTER)

        title = Gtk.Label(label="SpiteBatt")
        title.set_xalign(0.5)
        title.get_style_context().add_class("title-1")

        subtitle = Gtk.Label(label="Choose how your battery should behave")
        subtitle.set_xalign(0.5)
        subtitle.set_wrap(True)
        subtitle.set_justify(Gtk.Justification.CENTER)
        subtitle.set_margin_bottom(10)

        profiles = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=PROFILES_GAP)
        profiles.set_halign(Gtk.Align.CENTER)
        profiles.set_margin_top(6)
        profiles.set_margin_bottom(18)

        # Home column
        home_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        home_col.set_size_request(COL_WIDTH, -1)
        home_col.set_halign(Gtk.Align.CENTER)

        home_desc = Gtk.Label(label="Optimized for long battery health when plugged in")
        home_desc.set_wrap(True)
        home_desc.set_justify(Gtk.Justification.CENTER)
        home_desc.set_xalign(0.5)
        home_desc.set_max_width_chars(WRAP_CHARS)
        home_desc.set_width_chars(WRAP_CHARS)

        btn_home = Gtk.Button(label="Home")
        btn_home.set_size_request(BTN_WIDTH, -1)
        btn_home.set_hexpand(False)
        btn_home.set_halign(Gtk.Align.CENTER)

        home_col.append(home_desc)
        home_col.append(btn_home)

        # Travel column
        travel_col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        travel_col.set_size_request(COL_WIDTH, -1)
        travel_col.set_halign(Gtk.Align.CENTER)

        travel_desc = Gtk.Label(label="Full charge for travel and long days away")
        travel_desc.set_wrap(True)
        travel_desc.set_justify(Gtk.Justification.CENTER)
        travel_desc.set_xalign(0.5)
        travel_desc.set_max_width_chars(WRAP_CHARS)
        travel_desc.set_width_chars(WRAP_CHARS)

        btn_travel = Gtk.Button(label="On-the-go")
        btn_travel.set_size_request(BTN_WIDTH, -1)
        btn_travel.set_hexpand(False)
        btn_travel.set_halign(Gtk.Align.CENTER)

        travel_col.append(travel_desc)
        travel_col.append(btn_travel)

        profiles.append(home_col)
        profiles.append(travel_col)

        active_label = Gtk.Label(label="Active profile: Not set yet")
        active_label.set_xalign(0.5)
        active_label.set_margin_top(8)

        status = Gtk.Label(label=DEFAULT_STATUS)
        status.set_xalign(0.5)
        status.set_wrap(True)
        status.set_justify(Gtk.Justification.CENTER)
        status.set_margin_top(8)

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

        btn_home.connect("clicked", lambda _b: (run_profile("home", status), apply_active_ui()))
        btn_travel.connect("clicked", lambda _b: (run_profile("travel", status), apply_active_ui()))

        content.append(title)
        content.append(subtitle)
        content.append(profiles)
        content.append(active_label)
        content.append(status)

        outer.append(content)
        win.set_child(outer)
        win.present()

        apply_active_ui()
        GLib.timeout_add_seconds(2, apply_active_ui)
