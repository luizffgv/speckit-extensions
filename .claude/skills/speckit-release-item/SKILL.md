---
name: speckit-release-item
description: Bump an item's version, changelog and catalog for release.
when_to_use: After changing an already-released extension, preset, workflow or step type, when validation reports "content changed since release", or when asked to release, publish or bump an item.
---

# Release a new version of an item

Releases happen automatically: when a commit on `main` lists a version in a
`catalog.json` that has no tag yet, CI creates a GitHub release tagged
`<kind>-<id>-v<version>` (with a zip for extensions and presets), marked as a
pre-release for `0.x` and `-suffix` versions. This skill only gets the
change ready to merge. Never create tags or releases by hand, and don't push
unless the user asks.

## Steps

1. **Find what changed** since the last release of each touched item:
   ```bash
   git tag -l '<kind>-<id>-v*' --sort=-v:refname | head -1
   git diff <that-tag> -- <kind>s/<id>/
   ```
   `uv run scripts/repo.py validate` lists every released item whose content
   changed ("content changed since release ...; bump the version").
2. **Choose the bump** (semver), and confirm it with the user if unsure:
   - **major:** breaking. A command, input, config key or output was renamed or
     removed; behaviour changed incompatibly; `requires.speckit_version` was raised
     past what users likely have.
   - **minor:** new command, hook, input, config key or output, or a
     backwards-compatible behaviour change.
   - **patch:** fixes, wording, docs.
3. **Bump the version** in the manifest: `extension.version` in `extension.yml`,
   `preset.version` in `preset.yml`, `workflow.version` in `workflow.yml`, or `step.version` in
   `step.yml`.
4. **Add a changelog entry** at the top of the item's `CHANGELOG.md`:
   `## X.Y.Z` followed by short bullets that say what users notice.
5. **Validate and regenerate**:
   ```bash
   uv run scripts/repo.py validate
   uv run scripts/repo.py catalog
   ```
6. **Commit** the item and the updated `catalog.json` together, only when the
   user asks you to commit.

## Notes

- One version per change set: if an item was already bumped and not yet
  released (no tag for it), don't bump it again; add to its changelog entry.
- Items that aren't released yet (no tag for the current version) can be edited
  freely.
- Catalogs list only each item's current version.
- Checksums in the catalog come from the source, so regenerate the catalog after
  every edit. CI fails if it is stale.
