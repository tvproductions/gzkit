# Documentation Structure

```
docs/
├── user/           # Public site (gzkit.org) - served by MkDocs
│   ├── index.md
│   ├── charter.md
│   ├── lineage.md
│   └── ...
├── developer/      # Internal docs - NOT published
│   ├── deployment.md
│   └── ...
└── README.md       # This file
```

## Editing

- **Public docs**: Edit `docs/user/`, run `uv run mkdocs serve` to preview
- **Internal docs**: Edit `docs/developer/`, no build needed

## Build

```bash
uv sync --extra docs
uv run mkdocs build    # Output to site/
uv run mkdocs serve    # Dev server at localhost:8000
```
