# Mather Content

Versioned public learning content for [Mather](https://github.com/ganesh47/mather). Content releases are independent of app releases. This initial pack serves the Apple TV Memory Gallery.

## Download

The app checks this stable URL when entering the gallery chooser:

https://raw.githubusercontent.com/ganesh47/mather-content/main/memory-gallery/pack.json

JSON and its PNGs live together in `memory-gallery/`. The initial release is content version **2**, schema version **1**, with **76 cards and 82 images**. Installed apps validate hashes and cache complete packs for offline use. No API token is required.

Historical releases use tags such as `memory-gallery-v2`. Use the tag in place of `main` in the raw URL to retrieve a fixed release. Keep published tags unchanged. The app's main-branch URL receives later versions automatically.

## Author and publish

1. Create a branch and edit `memory-gallery/pack.json`. Preserve card IDs when correcting existing cards.
2. For new artwork, add a PNG, an asset entry, and a record in `memory-gallery/attribution.json`. PNG names must be `ASSET_ID.png`. When replacing artwork, use a new asset ID and filename, then update all references. Keep old files in Git so downloads using an earlier manifest can finish.
3. Increase `contentVersion`. Keep `schemaVersion` at `1` for the existing format and game mechanics.
4. Run `python3 scripts/validate_pack.py --rehash` if images changed, then `python3 scripts/validate_pack.py`. Review facts and artwork manually; validation does not establish factual accuracy.
5. Open a pull request. CI verifies structure, image sizes, hashes, required credits, and a version increase. Merge the reviewed PR to `main` to publish. Publish a GitHub release using the matching `memory-gallery-vN` tag to mark the version.

To roll back, restore previous content and publish it with a **higher** content version. Apps ignore equal or lower versions.

The validator uses Python's standard library and has no dependency on the Mather app repository. The client performs additional PNG decoding checks. It supports four existing decks: `domesticAnimals`, `vehicles`, `planets`, and `countryFlags`. New mechanics or categories require a compatible app update.

## Format

A pack has `schemaVersion`, `contentVersion`, `decks`, and `assets`. Decks contain `kind` and `cards`. Cards contain `id`, `name`, `canonicalName`, `picture`, `metadata`, and `learningArtwork`.

Pictures contain `kind` (`asset`, `emoji`, or `text`) and `value`. Metadata contains `deck`, `category`, `kind`, and `factCards`; each fact has `title` and `value`. Country cards require Capital, Language, Currency, and Monument facts. Preserve these fact titles because the client uses them for questions. Learning artwork contains `title` and `assetName`.

Assets contain `id`, `file`, `byteCount`, and a lowercase hexadecimal `sha256`. Published packs include every referenced image. IDs use ASCII letters, digits, hyphens, and underscores.

Limits: 4–250 cards per deck, unique card IDs, 1–12 facts per card, required text up to 500 characters, four learning illustrations per card, 200 images total, 10 MB per PNG, 100 MB total artwork, 4096 pixels per image dimension, and 5 MB JSON. The app's schema validation is authoritative.

## Credits and rights

`memory-gallery/attribution.json` preserves the original sources, creators, credit lines, usage terms, and transformations for supplied images, including NASA-hosted planetary imagery. This repository's public visibility does not grant a blanket license over all content. Project-owned content remains the owner's property; third-party imagery retains its stated source terms. No license is granted beyond those terms.
