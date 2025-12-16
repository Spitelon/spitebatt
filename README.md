# SpiteBatt 🦇🔋

**SpiteBatt** is a small, simple GTK application for Linux Mint (and similar
distributions) that lets you quickly switch between battery charging profiles
with a single click.

It is designed for users who want **full control over battery charging limits**
without touching the terminal or editing configuration files.

---

## What SpiteBatt does

SpiteBatt provides two clear profiles:

- **Home**
  - Limits battery charging (for example 40–80%)
  - Helps preserve long-term battery health when plugged in most of the time

- **On-the-go**
  - Allows full charging (0–100%)
  - Ideal for travel or long days away from a charger

You select a profile from a simple GUI, and the change is applied immediately.

---

## TLP usage (important)

SpiteBatt uses **TLP only for battery charge thresholds**.

- TLP is **not** used for:
  - CPU tuning
  - Power governors
  - Disk or PCI power management
  - Any other system-level optimizations

SpiteBatt applies only:
- `tlp setcharge`
- `tlp start`

This ensures:
- No interference with existing system settings
- No unexpected power-management behavior
- Safe coexistence with other tools or default Mint power profiles

---

## Requirements

- Linux Mint (tested) or other GTK-based Linux distributions
- Python 3
- TLP
- GTK 4 (PyGObject)

Install dependencies:
```bash
sudo apt install python3 python3-gi gir1.2-gtk-4.0 tlp
