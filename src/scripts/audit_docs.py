"""
Automated CI/CD script to audit the Project Architecture mapping.
Asserts that every Python file has exactly 1 matching domain tag,
and that every tag listed in the markdown map actually exists in code.

@Architecture-Map: [SCRIPT-AUDIT-DOCS]
@Docs: docs/reference/07_ARCHITECTURE_MAP.md
"""
import os
import re
import sys

SRC_DIR = "src"
MAP_FILE = "docs/reference/07_ARCHITECTURE_MAP.md"

def main():
    if not os.path.exists(MAP_FILE):
        print(f"❌ Error: {MAP_FILE} not found. (Did you move it?)")
        sys.exit(1)

    with open(MAP_FILE, "r", encoding="utf-8") as f:
        map_content = f.read()

    # Regex: extract [TAG] and src/.../file.py
    entries = re.findall(r'-\s*\*\*`\[([^\]]+)\]`\*\*:?\s*`(src/[a-zA-Z0-9_/\-\.]+py)`', map_content)
    map_dict = {tag: path for tag, path in entries}
    inverse_map_dict = {path: tag for tag, path in entries}

    all_py_files = []
    for root, dirs, files in os.walk(SRC_DIR):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Normalize slashes (windows vs linux)
                path = os.path.join(root, file).replace("\\", "/")
                all_py_files.append(path)

    errors = []

    # 1. Audit codebase against the Map
    for py_file in all_py_files:
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()

        tag_match = re.search(r'@Architecture-Map:\s*\[([^\]]+)\]', content)
        if not tag_match:
            errors.append(f"MISSING TAG: {py_file} does not contain an @Architecture-Map docstring.")
            continue

        tag = tag_match.group(1)

        if py_file not in inverse_map_dict:
            errors.append(f"UNMAPPED FILE: {py_file} claims tag [{tag}] but is NOT mapped in {MAP_FILE}.")
        elif inverse_map_dict[py_file] != tag:
            expected_tag = inverse_map_dict[py_file]
            errors.append(f"MISMATCH: {py_file} has tag [{tag}] but '{MAP_FILE}' expects [{expected_tag}].")

    # 2. Audit Map against the codebase
    for tag, expected_path in map_dict.items():
        if expected_path not in all_py_files:
            errors.append(f"DEAD LINK: '{MAP_FILE}' expects '{expected_path}' for tag [{tag}], but that Python file does not exist.")

    if errors:
        print("\n❌ Architecture Map Audit FAILED:")
        for e in errors:
            print(f"  - {e}")
        print("\nFix these discrepancies before committing.")
        sys.exit(1)
    else:
        print(f"✅ Architecture Map Audit PASSED! All {len(all_py_files)} files accounted for.")
        sys.exit(0)

if __name__ == "__main__":
    main()
