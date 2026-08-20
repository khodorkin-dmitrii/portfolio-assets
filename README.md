# Portfolio Assets

This repository is public infrastructure for versioned static assets and machine-readable manifests used by portfolio applications. GitHub Pages can publish the committed files directly, without a site generator or build step.

Public site: [khodorkin-dmitrii.github.io/portfolio-assets](https://khodorkin-dmitrii.github.io/portfolio-assets/)

Keeping assets here separates potentially large, independently versioned media from application source code and releases. Each consumer owns an isolated namespace under `projects/<project-id>/`, so one project's manifest and naming decisions do not affect another.

## Repository layout

```text
.
├── projects/
│   └── holocron/
│       ├── images/
│       ├── manifest.json
│       └── README.md
├── scripts/
│   └── validate_assets.py
├── .github/workflows/validate-assets.yml
├── .nojekyll
└── index.html
```

The expected Pages base URL is:

```text
https://khodorkin-dmitrii.github.io/portfolio-assets/
```

Project manifests are available beneath that base URL. The initial Holocron manifest will be:

```text
https://khodorkin-dmitrii.github.io/portfolio-assets/projects/holocron/manifest.json
```

A versioned asset URL will look like:

```text
https://khodorkin-dmitrii.github.io/portfolio-assets/projects/holocron/images/people/1/tatooine-farmboy-card-v1.webp
```

These public URLs will not work until the changes are pushed and GitHub Pages is enabled.

## Asset model

An **artwork** is a distinct visual representation of an entity. A **variant** is a technical presentation of the same artwork. For example, `tatooine-farmboy` and `jedi-knight` are separate artworks; each can have a `card` variant for lists and a `full` variant for galleries or dossiers. Clients can use the first artwork by `displayOrder` for catalog presentation without a duplicated `primaryImageUrl` field.

Files use this form:

```text
<artwork-id>-<variant>-v<asset-version>.<extension>
```

Use lowercase kebab-case semantic artwork IDs, `card` or `full` as the variant, and explicit versions such as `v1`. WebP is preferred for runtime assets; PNG or JPEG should be used only for a concrete reason. When pixels or encoding change, normally create a new versioned filename. Keep previously published files while released clients may reference them: versioned names provide cache busting while preserving stable old URLs.

Manifest paths are relative to the manifest itself. They must remain within the project namespace and must not be absolute URLs.

## Add a future project

1. Create `projects/<project-id>/manifest.json` and an adjacent project README.
2. Keep its images below `projects/<project-id>/images/`.
3. Start with the supported manifest schema and a project-owned `contentVersion`.
4. Extend validation deliberately if the project introduces a different entity model or naming rule.
5. Add the project and manifest link to `index.html`.
6. Run validation before review.

Do not combine project records into a global asset manifest.

## Add an entity artwork

1. Confirm the entity category and external resource ID from an authoritative source; do not infer identity from a filename.
2. Prepare matching `card` and `full` files using a stable artwork ID and versioned filenames.
3. Place them in the project-specific category and numeric-ID directory.
4. Add one artwork record containing both variants to that project's manifest.
5. Keep entities ordered by type and numeric ID, and artworks ordered by `displayOrder`.
6. Increment that manifest's `contentVersion` whenever mappings, ordering, paths, or metadata change.
7. Run `python scripts/validate_assets.py`.

The `schemaVersion` changes only for a breaking contract change. The `contentVersion` is a positive project-local revision for compatible content changes. Do not add volatile timestamps.

## Validation

Python 3 and only its standard library are required. From the repository root, run:

```bash
python scripts/validate_assets.py
python -m json.tool projects/holocron/manifest.json
```

The GitHub Actions workflow runs the same validator for pull requests, pushes to `main`, and manual dispatches. It validates content only; it does not deploy Pages.

## Enable GitHub Pages

After committing and pushing to `main`, configure the repository manually:

1. Open **Settings → Pages**.
2. Under **Build and deployment**, set **Source** to **Deploy from a branch**.
3. Select branch **main** and folder **/ (root)**.
4. Save, wait for publication, then verify the landing page and manifest URLs above.

The empty `.nojekyll` file ensures Pages serves the repository as plain static content.

## Public-content policy and scope

Everything committed here should be assumed public, downloadable, and cacheable. Never commit credentials, secrets, private files, source PSDs with private metadata, or assets without redistribution permission. Review embedded metadata before publishing source material.

An MIT `LICENSE` already exists in this repository and has been preserved. Third-party assets can have separate rights and must not be introduced without explicit redistribution permission and any required notices. Attribution metadata may be added compatibly before licensed third-party content is published.

Current scope is static images, project manifests, documentation, and lightweight validation. This repository intentionally has no image build pipeline, automatic manifest generation, client networking code, backend, JavaScript application, analytics, service worker, Git LFS, CDN integration, deployment workflow, or global multi-project API. Image conversion, thumbnails, release automation, a custom domain, and a full gallery site remain separate future decisions.
