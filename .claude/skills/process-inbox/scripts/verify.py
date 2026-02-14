#!/usr/bin/env python3
"""Verify process-inbox skill."""
import os
import re
import sys

def main():
    skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_md = os.path.join(skill_path, "SKILL.md")

    if not os.path.isfile(skill_md):
        print(f"✗ SKILL.md not found at {skill_path}")
        sys.exit(1)

    with open(skill_md, 'r') as f:
        content = f.read()

    # Extract YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        print("✗ Missing YAML frontmatter")
        sys.exit(1)

    frontmatter = match.group(1)

    # Check name
    name_match = re.search(r'^name:\s*(.+)$', frontmatter, re.MULTILINE)
    if not name_match or 'process-inbox' not in name_match.group(1):
        print("✗ Invalid name")
        sys.exit(1)

    # Check description
    desc_match = re.search(r'^description:\s*[\|>]?\s*\n?(.*)', frontmatter, re.MULTILINE | re.DOTALL)
    if not desc_match or 'use when' not in desc_match.group(1).lower():
        print("✗ Description missing 'Use when' trigger")
        sys.exit(1)

    print("✓ process-inbox valid")
    sys.exit(0)

if __name__ == "__main__":
    main()
