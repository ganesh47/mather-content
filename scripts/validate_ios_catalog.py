#!/usr/bin/env python3
"""Validate the separate iOS catalog; TV keeps its four-deck contract."""
import json
from pathlib import Path
from validate_pack import ID, require, validate

DECKS = {"domesticAnimals", "birds", "vehicles", "planets", "fishes", "countries", "countryFlags", "indiaStates", "waterCycle", "fruits", "numberBondsTo10"}
TOPICS = {"countries", "fruits", "water-cycle", "shapes", "electronics", "world-animals", "world-birds"}
BUNDLED_VECTORS = {"Electronics" + name for name in ("Battery", "Bulb", "Wire", "Switch", "ClosedCircuit", "OpenCircuit", "SafeCircuit", "OutletSafety")}
BUNDLED_BIRDS = {f"MemoryBird{sheet}{index:02d}" for sheet in "AB" for index in range(1,19)}
KINDS = {"flashcards", "easyMemory", "flipMemory", "bondBlast", "multipleChoice"}
SHAPES = {"country-" + name for name in ("india", "japan", "france", "egypt", "brazil", "australia", "canada", "kenya", "united-states", "united-kingdom", "china", "germany", "mexico", "south-africa", "italy", "saudi-arabia")}

def text(value):
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 1000

def identifier(value):
    return isinstance(value, str) and ID.fullmatch(value)

def check(path=Path("ios/catalog.json")):
    validate(path, required_decks=DECKS, bundled_assets=BUNDLED_BIRDS | BUNDLED_VECTORS)
    data = json.loads(path.read_text())
    threads = data["threads"]
    require(len(threads) == len(TOPICS) and {t["id"] for t in threads} == TOPICS, "Expected seven distinct topics")
    assets = {a["id"] for a in data["assets"]}
    def visual(item):
        if item.get("visualAssetName") is not None:
            require(item["visualAssetName"] in assets | BUNDLED_VECTORS | BUNDLED_BIRDS, "Topic artwork missing")
        if item.get("visualShapeKey") is not None:
            require(item["visualShapeKey"] in SHAPES, "Unsupported shape")
        if item.get("visualKey") is not None:
            require(text(item["visualKey"]), "Invalid visual label")
    for thread in threads:
        require(text(thread["title"]) and identifier(thread["category"]["id"]) and text(thread["category"]["title"]), "Invalid topic")
        types = thread["propertyTypes"]
        type_ids = {p["id"] for p in types}
        require(1 <= len(types) <= 24 and len(type_ids) == len(types), "Invalid property types")
        require(all(identifier(p["id"]) and text(p["displayName"]) and text(p["prompt"]) for p in types), "Invalid type")
        entities = thread["entities"]
        require(2 <= len(entities) <= 250 and len({e["id"] for e in entities}) == len(entities), "Invalid entities")
        prop_ids = set()
        for entity in entities:
            require(identifier(entity["id"]) and text(entity["name"]) and len(entity["summary"]) <= 1000, "Invalid entity")
            visual(entity)
            require(1 <= len(entity["properties"]) <= 24, "Invalid properties")
            for prop in entity["properties"]:
                require(identifier(prop["id"]) and prop["id"] not in prop_ids and prop["typeID"] in type_ids, "Invalid property identity")
                prop_ids.add(prop["id"])
                require(text(prop["value"]) and len(prop["explanation"]) <= 1000, "Invalid property text")
                visual(prop)
        stages = thread["stages"]
        require(1 <= len(stages) <= 12 and len({s["id"] for s in stages}) == len(stages), "Invalid stages")
        for stage in stages:
            require(identifier(stage["id"]) and stage["kind"] in KINDS and text(stage["title"]) and text(stage["prompt"]), "Invalid stage")
            require(type(stage["maximumItemCount"]) is int and 1 <= stage["maximumItemCount"] <= 100 and set(stage["propertyTypeIDs"]) <= type_ids, "Invalid stage selection")
    print(f"Valid iOS catalog: {len(threads)} topics")

if __name__ == "__main__":
    check()
