# Living Specs

The current behavior of this project, one spec per capability. Feature directories under
`specs/` (`specs/NNN-*`) and retired specs under `specs/retired/` are history: read them only to
learn why something changed. Updated by `speckit.living.sync`; edit a spec's text through a
feature's deltas, not by hand.

| Spec | Covers |
| --- | --- |
| [add-task](add-task/spec.md) | Adding tasks: titles trimmed, 1–200 characters, sequential IDs never reused, storage. |
| [list-tasks](list-tasks/spec.md) | Listing tasks: order added, "<ID>. <title>" lines, "No tasks." when empty. |
