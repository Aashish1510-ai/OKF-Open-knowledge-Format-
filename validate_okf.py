
from pathlib import Path

ROOT = Path(__file__).parent

markdown_files = [
    p for p in ROOT.rglob("*.md")
    if not any(part.startswith(".") for part in p.relative_to(ROOT).parts)
]

errors = []

print("OKF Knowledge Bundle Validator")
print("=" * 35)

for file_path in markdown_files:
    relative_path = file_path.relative_to(ROOT)
    content = file_path.read_text(encoding="utf-8-sig")
    lines = content.splitlines()

    print(f"\nChecking: {relative_path}")

    # Check opening and closing frontmatter
    if not lines or lines[0].strip() != "---":
        errors.append(f"{relative_path}: First line must be ---")
        continue

    try:
        closing = next(
            i for i in range(1, len(lines))
            if lines[i].strip() == "---"
        )
    except StopIteration:
        errors.append(f"{relative_path}: Closing --- not found")
        continue

    metadata_lines = lines[1:closing]
    body = "\n".join(lines[closing + 1:])

    # Read required metadata
    fields = {}
    for line in metadata_lines:
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')

    if file_path.name != "index.md":
        for key in ("type", "title", "description"):
            if not fields.get(key):
                errors.append(
                    f"{relative_path}: Missing metadata: {key}"
                )

    # Check Markdown links
    for part in body.split("](")[1:]:
        target = part.split(")", 1)[0].strip()

        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue

        target = target.split("#", 1)[0].split("?", 1)[0]

        if target and not (file_path.parent / target).exists():
            errors.append(f"{relative_path}: Broken link -> {target}")

print("\n" + "=" * 35)
print(f"Markdown files checked: {len(markdown_files)}")
print(f"Errors: {len(errors)}")

if errors:
    for error in errors:
        print("-", error)
    print("\nValidation FAILED.")
else:
    print("\nValidation PASSED.")
