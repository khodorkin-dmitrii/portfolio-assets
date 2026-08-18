# Holocron of Balance assets

`holocron` is the isolated asset namespace for the Holocron of Balance application. Its manifest is `manifest.json`, and all referenced paths resolve relative to this directory.

Holocron supports six SWAPI-compatible entity types:

| Manifest `type` | Image directory |
| --- | --- |
| `film` | `images/films/` |
| `person` | `images/people/` |
| `planet` | `images/planets/` |
| `species` | `images/species/` |
| `starship` | `images/starships/` |
| `vehicle` | `images/vehicles/` |

Directories use the positive numeric SWAPI **resource ID**, not a display name. For films, the SWAPI resource ID is not the same thing as `episode_id`; never infer a film identity from its episode number.

## Manifest v1

The real manifest starts valid and empty. Its top-level contract is:

- `schemaVersion`: `1`, changed only by a breaking JSON-contract revision.
- `contentVersion`: a positive integer incremented for compatible content, mapping, ordering, path, or metadata changes.
- `projectId`: the stable value `holocron`.
- `entities`: entity-to-artwork mappings, deterministically ordered by type and numeric ID.

An entity uses a singular lowercase `type` from the table above and a positive numeric SWAPI resource `id`. Each `(type, id)` pair is unique.

Each entry in `images` represents a distinct artwork, not a file. Its semantic lowercase kebab-case `id` is unique within the entity. `displayOrder` is a unique non-negative integer within the entity and controls gallery order; catalog clients normally select the first artwork. An optional English `label` distinguishes artworks but is not localized accessibility text.

Every artwork has both `card` and `full` variants of the same visual representation. `card` is intended for catalog/list presentation; `full` is intended for dossier/gallery presentation. Variant paths are relative to this README's directory and `manifest.json`, remain inside the `holocron` namespace, and include positive pixel dimensions.

### Illustrative example only

The following complete entity is documentation, not real manifest data. The referenced files do not exist yet and this record must not be added until they do.

```json
{
  "type": "person",
  "id": 1,
  "images": [
    {
      "id": "tatooine-farmboy",
      "label": "Young farm boy",
      "displayOrder": 0,
      "variants": {
        "card": {
          "path": "images/people/1/tatooine-farmboy-card-v1.webp",
          "width": 512,
          "height": 768
        },
        "full": {
          "path": "images/people/1/tatooine-farmboy-full-v1.webp",
          "width": 1024,
          "height": 1536
        }
      }
    },
    {
      "id": "jedi-knight",
      "label": "Jedi Knight",
      "displayOrder": 1,
      "variants": {
        "card": {
          "path": "images/people/1/jedi-knight-card-v1.webp",
          "width": 512,
          "height": 768
        },
        "full": {
          "path": "images/people/1/jedi-knight-full-v1.webp",
          "width": 1024,
          "height": 1536
        }
      }
    }
  ]
}
```

Two life periods above are two artworks. The `card` and `full` files inside each record are technical variants of one artwork, so no separate primary-image field is needed.

## Paths and filenames

Use `images/<plural-category>/<resource-id>/<artwork-id>-<variant>-v<asset-version>.<extension>`. IDs and filenames are lowercase kebab-case. Prefer WebP; PNG or JPEG requires a concrete reason. Create a new filename version when content changes, keep old published URLs while clients may use them, and never use `..`, absolute URLs, queries, or fragments in the manifest.

After GitHub Pages is enabled, expected URLs include:

```text
https://khodorkin-dmitrii.github.io/portfolio-assets/projects/holocron/manifest.json
https://khodorkin-dmitrii.github.io/portfolio-assets/projects/holocron/images/people/1/tatooine-farmboy-card-v1.webp
```

Attribution metadata may be added compatibly before third-party licensed assets are introduced. Holocron of Balance is an unofficial fan and educational project. Do not add official logos, copied official artwork, or any asset without redistribution permission.

