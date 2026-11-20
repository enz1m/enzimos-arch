# Testing on a real Arch-based distribution

The VM uses KVM and QEMU's `virtio-vga-gl` display. The disk and firmware
variables live under `${XDG_STATE_HOME:-$HOME/.local/state}/enzimos-arch/vm`.
Set `ENZIMOS_ARCH_VM` to use a different directory.

## 1. Install the distribution once

Download a verified installation ISO and keep it outside the checkout.

```sh
test/vm install /path/to/installer.iso
```

Install it normally with the graphical installer (erase disk, one user, no
encryption needed). Shut down, then keep the clean system:

```sh
test/vm snapshot clean
```

## 2. Serve a repository

Build one (see the main README), then on the host:

```sh
test/serve-repo OUT/repo          # http://10.0.2.2:18093/ from the VM
```

## 3. Install enzimOS in the VM

```sh
test/vm run
```

In the VM, copy `enzimos-try` and `enzimos-packages.asc` over (for example
`curl -O http://10.0.2.2:18093/enzimos-packages.asc` and the tool from a
second `python3 -m http.server` in this repository), then:

```sh
sudo ENZIMOS_REPO_URL=http://10.0.2.2:18093/enzimos/x86_64 \
     ENZIMOS_KEY_FILE=enzimos-packages.asc \
     ENZIMOS_KEY_FINGERPRINT=316DD17C64DB52ABEFA9B558AA8B1E969F33214C \
     ./enzimos-try install --apps
```

Log out; choose "enzUI" in the login manager's session menu.

## 4. Checklist

| Check | Expect |
|---|---|
| `pacman -Syu` during install | completes; no partial upgrade, no D-Bus implementation switch prompt |
| Credential provider | existing GNOME Keyring/KWallet/oo7 and login-manager PAM files are preserved; saved credentials still unlock |
| Login manager | lists enzUI next to the existing desktop |
| enzUI session | bar, launcher, Settings open; Files, Terminal, Store launch |
| Settings pages | pages for unavailable services are hidden and available pages open |
| Network page | works with NetworkManager; hidden with iwd-only or systemd-networkd |
| Store | lists Flathub and enzimOS apps; installs one; updates |
| Back in the original desktop | its config untouched: `~/.config/hypr`, `~/.local/share/hyprland`, default apps, autostart |
| `sudo enzimos-try remove` | removes only installer-owned additions and its repository/key; pre-existing packages (including orphans) and the original desktop still work |

Go back to the clean system between runs:

```sh
test/vm revert clean
```

## Preservation and failure cases

Run these in the disposable guest, with an existing Plasma/SDDM login and
credential provider established before installing enzUI:

- Save `pacman -Qq` and `pacman -Qqe`, the original desktop's configuration,
  `/etc/pacman.conf`, and the display manager's PAM file. Store a test credential
  in the existing Secret Service provider and verify it from both desktops.
- Keep a pre-existing unused dependency, such as `xdg-desktop-portal-hyprland`
  marked with `pacman -D --asdeps`, and confirm removal preserves it and its reason.
- Install with `--apps`, log into enzUI through SDDM, exercise shell/Settings,
  theme switching, a portal file chooser, lock/unlock, screenshots and native apps.
- Use the shell's actual Log out button. The greeter must return without restarting
  SDDM; choose Plasma and verify the original desktop again.
- Install an independent app through Store, then remove enzUI from Plasma.
  Its shared Flatpak runtime must remain usable. Original package names and
  install reasons, KDE configuration, SDDM/PAM, documents and credentials stay.
- Repeat install/remove; a preconfigured repository/key must not be adopted.
  Test an unreachable repository on a fresh install: failure must remove only
  that attempt's repository/key so normal pacman updates remain usable.
- Never use a successful launch after manually restarting the display manager as
  proof that logout works. Check optional hardware features separately on hardware.

## Distributions to cover

| Distribution | Why |
|---|---|
| Arch | the build target; library versions match |
| Manjaro stable | check the package and library versions available on the target release |
| EndeavourOS | Arch repositories, different defaults (no NetworkManager applet choice, SDDM) |
| CachyOS | Arch with its own optimised repositories |
