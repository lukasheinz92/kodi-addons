"""Build the Kodi repository site (GitHub Pages) from the add-on folders in this repo.

Every top-level folder containing an addon.xml is an add-on. Output (default: _site/):
  addons.xml, addons.xml.md5        - what Kodi reads to find add-ons and updates
  <id>/<id>-<version>.zip           - add-on packages (layout expected by <datadir zip="true">)
  repository.*-<version>.zip        - repository add-on also at the root, for "Install from zip file"
  index.html (root and per add-on)  - browsable listings for Kodi's file manager (link text == href)

Usage: python tools/build.py [output_dir]
"""
import hashlib
import html
import os
import shutil
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXCLUDE_DIRS = {"__pycache__", ".git", ".idea", ".vscode"}
EXCLUDE_EXT = {".pyc", ".pyo"}


def find_addons():
    addons = []
    for name in sorted(os.listdir(ROOT)):
        path = os.path.join(ROOT, name)
        xml_path = os.path.join(path, "addon.xml")
        if name.startswith((".", "_")) or not os.path.isfile(xml_path):
            continue
        root = ET.parse(xml_path).getroot()
        addon_id, version = root.get("id"), root.get("version")
        if addon_id != name:
            sys.exit("folder %r must be named after its add-on id %r" % (name, addon_id))
        addons.append((addon_id, version, path, xml_path))
    return addons


def zip_addon(addon_id, path, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
            for fn in sorted(filenames):
                if os.path.splitext(fn)[1] in EXCLUDE_EXT:
                    continue
                full = os.path.join(dirpath, fn)
                arc = os.path.join(addon_id, os.path.relpath(full, path)).replace(os.sep, "/")
                zf.write(full, arc)


def write_index(directory, entries):
    links = "\n".join('<a href="%s">%s</a><br>' % (html.escape(e), html.escape(e)) for e in entries)
    with open(os.path.join(directory, "index.html"), "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html>\n<html><head><meta charset=\"utf-8\"><title>kodi-addons</title></head>"
                "<body>\n%s\n</body></html>\n" % links)


def strip_declaration(text):
    text = text.strip()
    if text.startswith("<?xml"):
        text = text[text.index("?>") + 2:].strip()
    return text


def main():
    out = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "_site"))
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)

    addons = find_addons()
    parts, root_entries = [], []
    for addon_id, version, path, xml_path in addons:
        addon_dir = os.path.join(out, addon_id)
        os.makedirs(addon_dir)
        zip_name = "%s-%s.zip" % (addon_id, version)
        zip_addon(addon_id, path, os.path.join(addon_dir, zip_name))
        write_index(addon_dir, [zip_name])
        if addon_id.startswith("repository."):
            shutil.copy(os.path.join(addon_dir, zip_name), out)
            root_entries.append(zip_name)
        root_entries.append(addon_id + "/")
        with open(xml_path, encoding="utf-8") as f:
            parts.append(strip_declaration(f.read()))
        print("packaged %s %s" % (addon_id, version))

    addons_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<addons>\n'
                  + "\n".join(parts) + "\n</addons>\n").encode("utf-8")
    ET.fromstring(addons_xml)  # sanity check: well-formed
    with open(os.path.join(out, "addons.xml"), "wb") as f:
        f.write(addons_xml)
    with open(os.path.join(out, "addons.xml.md5"), "w", encoding="ascii") as f:
        # md5sum format; Kodi's CRepository::FetchChecksum needs a space or newline after the hash
        f.write("%s  addons.xml\n" % hashlib.md5(addons_xml).hexdigest())
    write_index(out, root_entries)
    open(os.path.join(out, ".nojekyll"), "w").close()
    print("site written to %s" % out)


if __name__ == "__main__":
    main()
