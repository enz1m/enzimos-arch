# Native host service builds

The **Build native host services** workflow builds App Permissions,
Background Apps, MCP Center, Phone Link and Remote Access for Arch x86-64. The
checked-in `sources.json` selects the exact signed GitHub commit, Rust
toolchain, package version and release number for each package. An entry's
`repo` names its GitHub repository when it differs from the package name.

To prepare an update, review the upstream commit, update its entry and sign
the change to this repository. Increase the package release number when a
rebuild changes bytes without changing the upstream version. GitHub runs the
workflow when the recipe or its inputs change on main. The same workflow can
be run manually from Actions.

The worker prepares an official Arch container and downloads the pinned
sources and locked Cargo inputs. Compilation and tests run offline inside the
container as a regular user. Each output consists of a Pacman archive, a
`build.json` identifying the source and package digest, and
`build-environment.txt` listing the installed Arch build dependencies. An
independent job attests the output files. These are candidates for release
review. The Pacman repository accepts a separately signed snapshot.

Remote Access ships as two packages from one source commit.
`enzimos-rust-remote-access` carries the binaries listed in the source's
`packaging/rust/runtime.json`. `enzimos-remote-access` carries the system
units, policies, the source's pacman hooks and the `enzimos-remote` launcher,
and depends on that exact runtime version. The build stops unless both entries
pin the same commit and toolchain. Increase both release numbers when changing
the commit.

Phone Link builds its Wayland workers using three checksummed protocol files
from the public Hyprland revision pinned by the enzimOS shell build. Keep that
revision and `phone-protocols.sha256` in sync when changing the compositor
protocols. The package includes the notices from those protocol files.

Before promotion, run `python3 -m unittest discover -s packaging -p
test_start_host.py` from the pinned Phone Link checkout in a disposable Arch
guest. The installed-launcher test uses Bubblewrap's user namespaces to stage
the system paths. The hosted build container runs the Phone Link Rust tests
with networking disabled and the standard container syscall restrictions.
