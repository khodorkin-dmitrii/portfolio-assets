# Repository instructions

- This repository serves public static assets. Every committed path may become part of a public URL contract.
- Preserve project isolation under `projects/<project-id>`; each project owns its manifest and images.
- Avoid renaming or deleting published files without considering existing clients. Use semantic, versioned filenames for changed content.
- Update the appropriate manifest for content changes and increment its `contentVersion` when mappings, ordering, paths, or metadata change.
- Run `python scripts/validate_assets.py` from the repository root before handing off changes.
- Never add secrets, private metadata, or assets without redistribution permission.
- Never infer an image's entity identity from an ambiguous filename; verify it from an authoritative source.
- Do not modify neighboring repositories unless a task explicitly requires cross-repository work.
- Do not add build frameworks, package managers, Git LFS, or dependencies without a demonstrated need.
- Do not commit or push unless explicitly requested.

