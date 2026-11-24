# enzimOS on Arch

Add an enzUI session to an existing Arch Linux installation. Choose it from
your current login manager alongside your usual desktop. Pacman continues to
manage system updates. Each signed repository build must match the library
versions available on its target distribution.

## Use

A fresh install uses the signed repository at `packages.enzim.dev` and verifies
its public key against the pinned production fingerprint. For a lab repository,
set `ENZIMOS_REPO_URL`, `ENZIMOS_KEY_FILE` and `ENZIMOS_KEY_FINGERPRINT` to
the matching test values. See the [VM testing guide](test/README.md).

```sh
sudo ./enzimos-try install              # desktop: session, Settings, Files, Terminal, Store
sudo ./enzimos-try install --apps       # plus Text and Task Manager
sudo ./enzimos-try install --ai         # plus the on-device assistant and voice typing
sudo ./enzimos-try install --models     # plus the base models (about 700 MB)
sudo ./enzimos-try install --flatpak-apps   # plus the enzimOS Flatpak apps
sudo ./enzimos-try install --greeter    # plus the enzimOS login screen (greetd), from the next boot
sudo ./enzimos-try install --replace-flatpaks   # uninstall Flatpak copies of Files, Text, ... (data kept)
sudo ./enzimos-try status
sudo ./enzimos-try remove
sudo ./enzimos-try remove --purge-user-data   # also delete enzUI's own settings
```

`install` adds the `[enzimos]` pacman repository and its key, requires signed
package and database files, completes
`pacman -Syu`, and then installs the chosen meta-packages from the same
repository snapshot. `remove` removes packages added by the add-on transaction, then
its own repository configuration and signing key. Pre-existing packages,
including unused dependencies, and settings in your home folder stay. If a
package installed later needs an enzimOS dependency, normal pacman dependency
checks retain it and keep the repository/journal for a later retry; no forced
removal or package replacement is used. The shared Flatpak runtime and its
required dependencies stay, so apps independently installed through Store
continue to work after removing the desktop.
The installer removes only the Flatpaks it installed with `--flatpak-apps`
that still come from the enzimOS remote. Independently installed Flatpaks stay.
`--replace-flatpaks` applies only to apps available in the selected or already
installed native package set.

The existing Secret Service provider (GNOME Keyring, KWallet or oo7) stays in
place. The compatibility repository excludes the enzimOS keyring provider and
packages declaring replacements or conflicts, so a whole-system upgrade cannot
replace GNOME Keyring through that repository.
Default installation adds an enzUI session without changing SDDM/GDM or their
PAM configuration. Only `--greeter` opts into changing the login manager.
The `--flatpak-apps` option installs the stable apps currently available from the
signed enzimOS Flatpak remote at `flatpak.enzim.dev`. Installations of the same
apps that are already present are preserved.

If a fresh install fails before adding packages (for example an unreachable
repository), it removes its newly added repository/key automatically. A completed
Arch system upgrade is not rolled back. An attempt that did add packages keeps
its journal so removal can account for them.

Older journals from the combined upgrade and install are limited to enzimOS
repository packages on removal. Installations without an ownership journal, or
with an interrupted journal, require manual review.

Phone Link is included as an optional service. Open Settings > Phone Link to
turn it on and pair the Android app. It remains off until enabled, and streaming
is suspended when the graphical session locks. Existing phone pairings are kept.

## Layout

| Path | What |
|---|---|
| `enzimos-try` | the install / remove tool |
| `packaging/PKGBUILD` | meta-packages: `enzimos-desktop`, `enzimos-apps`, `enzimos-ai`, `enzimos-flatpak-remote` |
| `tools/build-desktop-package` | packages the enzUI session and optional greeter separately |
| `tools/build-repo` | collects the component packages from the enzimOS build, signs everything, writes the repository |
| `tools/build-os-repo` | adds the `enzimos-os` system repository that the installation media builder reads |
| `tools/check-sonames` | checks a distribution still provides the library versions the packages need |
| `test/` | a local repository server and a VM script for testing on a real distribution |

## Build a repository

See the [host-service build recipes](packaging/host-services/README.md) and
[desktop app source pins](packaging/native-apps/sources.json) for native CI.
Verify a completed app build with `tools/fetch-build-artifacts native-apps RUN_ID OUTPUT`.

Use a build machine that matches the target distribution's package libraries.
The desktop packager needs an enzUI desktop export and the enzimOS workspace's
packaging and export-validation helpers. The repository builder takes component
packages and their SHA-256 build reports from the enzimOS build.

```sh
mkdir -p "$PWD/out/meta"
tools/build-desktop-package /path/to/desktop-export out/desktop \
    --build-tools /path/to/enzimos-workspace/tools
meta_output="$PWD/out/meta"
(cd packaging && PKGDEST="$meta_output" makepkg --nodeps)
tools/build-repo --reports /path/to/component-build-reports \
    --desktop out/desktop --meta out/meta \
    --signer /path/to/signing-keyring --output out/repo
```

The desktop packager verifies the producer's file and link inventory.
The repository builder checks component archives against their build reports
before signing. Keep private signing keys outside the checkout. See
[`test/README.md`](test/README.md) to try a build in a VM.
For older build reports with workspace-relative archive paths, pass
`--workspace /path/to/enzimos-workspace` to `tools/build-repo`.

Pass `--profile desktop` to build a smaller repository with the session,
native apps and required services. The default `full` profile adds the
optional AI packages. Use `tools/check-sonames` with the target
distribution's sync databases before publishing a build.

## System repository

The [ISO builder](https://github.com/enz1m/enzimos-build) also reads the
signed `enzimos-os` repository at `packages.enzim.dev/enzimos-os/x86_64`. It
holds the installer, recovery and update runtimes, system policy, the
greetd, keyring and portal replacements, the local AI packages, the recovery
environment and two data packages: the staged desktop and the live installer
runtime layout. Arch systems never configure it.

```sh
tools/build-os-repo --reports /path/to/build-report.json ... \
    --desktop-stage /path/to/desktop --runtime-layout /path/to/runtime-layout \
    --release N --signer /path/to/gnupg --output /tmp/enzimos-os
python3 ../enzimos-arch-release/tools/repo_release.py bundle --signer /path/to/gnupg \
    --key 66CEB56F3018F39D2491A3B24C558611AFC55399 --parent ACTIVE_RELEASE \
    --repository /tmp/enzimos-os --published-db /tmp/enzimos-os/enzimos.db \
    --published-db PUBLISHED_ENZIMOS_OS_DB --output repository.tar.gz
```

Applications that are also in the add-on repository go into the system
repository only when their build is newer. The ISO builder takes the newest
version of each package across both repositories.

## Tests

```sh
tests/test-pacman-conf
tests/test-display-manager
tests/test-safeguards
```

## License

MIT
