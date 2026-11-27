#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remap iptv-org channel ids in generated EPG guides to the
Online4Tech (Khaled) xmltv ids used by our channels files.

Reads a mapping JSON: {"iptv-org-id": "khaled-xmltv-id", ...}
For every guide XML in --input-dir, renames <channel id="..."> and
<programme channel="..."> to the mapped id. Channels with no mapping
are dropped, so the output only contains channels our pack knows.

Usage:
  python3 remap-epg-ids.py --mapping id-mapping.json \
      --input-dir /tmp/guides --output-dir epg/guides

The mapping file is built after the full-coverage pack rebuild, from
the pack's channels XMLs + the iptv-org channels database.
"""
import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET


def remap_file(path, mapping, out_path):
    tree = ET.parse(path)
    root = tree.getroot()
    kept_channels = 0
    dropped_channels = 0
    for channel in list(root.findall("channel")):
        old_id = channel.get("id")
        new_id = mapping.get(old_id)
        if new_id is None:
            root.remove(channel)
            dropped_channels += 1
        else:
            channel.set("id", new_id)
            kept_channels += 1
    kept_programmes = 0
    dropped_programmes = 0
    for programme in list(root.findall("programme")):
        old_id = programme.get("channel")
        new_id = mapping.get(old_id)
        if new_id is None:
            root.remove(programme)
            dropped_programmes += 1
        else:
            programme.set("channel", new_id)
            kept_programmes += 1
    tree.write(out_path, encoding="utf-8", xml_declaration=True)
    return kept_channels, dropped_channels, kept_programmes, dropped_programmes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", required=True)
    parser.add_argument("--input-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    with open(args.mapping, encoding="utf-8") as f:
        mapping = json.load(f)
    print("mapping entries: %d" % len(mapping))

    os.makedirs(args.output_dir, exist_ok=True)
    for name in sorted(os.listdir(args.input_dir)):
        if not name.endswith(".xml"):
            continue
        src = os.path.join(args.input_dir, name)
        dst = os.path.join(args.output_dir, name)
        kc, dc, kp, dp = remap_file(src, mapping, dst)
        print("%s: channels kept %d dropped %d, programmes kept %d dropped %d"
              % (name, kc, dc, kp, dp))
    return 0


if __name__ == "__main__":
    sys.exit(main())
