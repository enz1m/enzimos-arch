# SPDX-License-Identifier: MIT
"""Check the Xwayland companion before creating a desktop package."""

from hashlib import file_digest
import json
from pathlib import Path
from stat import S_IMODE


def verify_xwayland(desktop, manifest):
    pin = manifest.get('pins', {}).get('xwayland')
    receipt = manifest.get('compositor', {}).get('xwayland')
    if not pin or not receipt or any(receipt.get(key) != value for key, value in pin.items()):
        raise SystemExit('desktop stage must include a locked Xwayland companion receipt')
    files = {row['path']: row for row in manifest['files']}
    for relative, mode, digest_key in (
        ('usr/lib/enzui/compositor/hyprland-current-build/Xwayland', 0o755, 'binary_sha256'),
        ('usr/share/licenses/enzui-desktop/Xwayland-COPYING', 0o644, 'notice_sha256'),
    ):
        path = desktop / relative
        row = files.get('/' + relative, {})
        checksum = receipt.get(digest_key)
        if (not checksum or row.get('type') != 'file' or row.get('sha256') != checksum
                or path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(desktop)
                or S_IMODE(path.stat().st_mode) != mode):
            raise SystemExit(f'desktop stage has a missing or unrecorded Xwayland file: {relative}')
        with path.open('rb') as source:
            if file_digest(source, 'sha256').hexdigest() != checksum:
                raise SystemExit(f'Xwayland file does not match the build receipt: {relative}')
    return receipt


def verify_stage_xwayland(desktop):
    desktop = Path(desktop).resolve(strict=True)
    manifest_path = desktop / 'usr/share/enzui/manifest.json'
    if not manifest_path.is_file():
        raise SystemExit('desktop stage is missing the Shell export manifest')
    return verify_xwayland(desktop, json.loads(manifest_path.read_text()))
