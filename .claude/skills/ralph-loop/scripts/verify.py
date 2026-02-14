#!/usr/bin/env python3
"""Verify ralph-loop skill."""
import os, re, sys
def main():
    skill_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.isfile(skill_md): print(f"✗ SKILL.md not found"); sys.exit(1)
    with open(skill_md, 'r') as f: content = f.read()
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match: print("✗ Missing YAML"); sys.exit(1)
    frontmatter = match.group(1)
    if not re.search(r'^name:\s*ralph-loop', frontmatter, re.MULTILINE): print("✗ Invalid name"); sys.exit(1)
    desc = re.search(r'^description:\s*[\|>]?\s*\n?(.*)', frontmatter, re.MULTILINE | re.DOTALL)
    if not desc or 'use when' not in desc.group(1).lower(): print("✗ No 'Use when'"); sys.exit(1)
    print("✓ ralph-loop valid"); sys.exit(0)
if __name__ == "__main__": main()
