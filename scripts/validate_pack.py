#!/usr/bin/env python3
"""Validate public Memory Gallery content without the Mather app or third-party libraries."""
import argparse
import hashlib
import json
import re
import struct
from pathlib import Path

ID = re.compile(r"[A-Za-z0-9_-]{1,100}\Z")
DECKS = {"domesticAnimals", "vehicles", "planets", "countryFlags"}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 500


def validate(path, rehash=False):
    require(path.stat().st_size <= 5_000_000, "Manifest exceeds 5 MB")
    pack = json.loads(path.read_text())
    require(pack["schemaVersion"] == 1, "Unsupported schema")
    require(type(pack["contentVersion"]) is int and pack["contentVersion"] > 1, "Published version must exceed bundled version 1")
    decks = pack["decks"]
    require(len(decks) == 4 and {d["kind"] for d in decks} == DECKS, "Expected four distinct gallery decks")
    assets = pack["assets"]
    require(len(assets) <= 200, "Too many assets")
    asset_ids = set()
    total = 0
    for asset in assets:
        name = asset["id"]
        require(isinstance(name, str) and ID.fullmatch(name), "Invalid asset ID")
        require(name not in asset_ids, f"Duplicate asset {name}")
        asset_ids.add(name)
        require(asset["file"] == f"{name}.png", f"Invalid path: {name}")
        image_path = path.parent / asset["file"]
        size = image_path.stat().st_size
        require(0 < size <= 10_000_000, f"Invalid image size: {name}")
        data = image_path.read_bytes()
        require(data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR", f"Invalid PNG: {name}")
        width, height = struct.unpack(">II", data[16:24])
        require(1 <= width <= 4096 and 1 <= height <= 4096, f"Invalid dimensions: {name}")
        digest = hashlib.sha256(data).hexdigest()
        if rehash:
            asset["byteCount"], asset["sha256"] = size, digest
        require(type(asset["byteCount"]) is int and asset["byteCount"] == size, f"Byte count mismatch: {name}")
        require(asset["sha256"] == digest, f"Hash mismatch: {name}")
        total += size
    require(total <= 100_000_000, "Artwork exceeds 100 MB")
    card_ids = set()
    for deck in decks:
        cards = deck["cards"]
        require(4 <= len(cards) <= 250, f"Invalid deck size: {deck['kind']}")
        for card in cards:
            name = card["id"]
            require(isinstance(name, str) and ID.fullmatch(name), "Invalid card ID")
            require(name not in card_ids, f"Duplicate card: {name}")
            card_ids.add(name)
            require(text(card["name"]) and text(card["canonicalName"]), f"Invalid name: {name}")
            meta = card["metadata"]
            require(meta["deck"] == deck["kind"], f"Deck mismatch: {name}")
            require(text(meta["category"]) and text(meta["kind"]), f"Invalid metadata: {name}")
            facts = meta["factCards"]
            require(1 <= len(facts) <= 12 and all(text(f["title"]) and text(f["value"]) for f in facts), f"Invalid facts: {name}")
            if deck["kind"] == "countryFlags":
                require({"capital", "language", "currency", "monument"} <= {f["title"].lower() for f in facts}, f"Missing country facts: {name}")
            picture = card["picture"]
            require(picture["kind"] in {"asset", "emoji", "text"} and text(picture["value"]), f"Invalid picture: {name}")
            if picture["kind"] == "asset":
                require(picture["value"] in asset_ids, f"Missing artwork: {name}")
            artwork = card["learningArtwork"]
            require(len(artwork) <= 4 and all(text(a["title"]) and a["assetName"] in asset_ids for a in artwork), f"Invalid learning artwork: {name}")
    credits = json.loads((path.parent / "attribution.json").read_text())
    require({c["assetName"] for c in credits} == asset_ids, "Every image needs an attribution record")
    for credit in credits:
        require(all(isinstance(credit.get(k), str) and credit[k].strip() for k in ("creator", "creditLine", "license")), "Incomplete image credit")
    if rehash:
        path.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n")
    print(f"Valid version {pack['contentVersion']}: {len(card_ids)} cards, {len(asset_ids)} PNGs, {total:,} image bytes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", nargs="?", type=Path, default=Path("memory-gallery/pack.json"))
    parser.add_argument("--rehash", action="store_true", help="Update PNG byte counts and hashes after artwork changes")
    args = parser.parse_args()
    validate(args.pack, args.rehash)
