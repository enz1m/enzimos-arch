# Native host service builds

The **Build native host services** workflow builds App Permissions,
Background Apps, MCP Center and Phone Link for Arch x86-64. The checked-in
`sources.json` selects the exact signed GitHub commit, Rust toolchain, package
version and release number for each service.

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

Phone Link builds its Wayland workers using three checksummed protocol files
from the public Hyprland revision pinned by the enzimOS shell build. Keep that
revision and `phone-protocols.sha256` in sync when changing the compositor
protocols. Native desktop integration is still checked in a disposable Arch
guest before promoting a release.
