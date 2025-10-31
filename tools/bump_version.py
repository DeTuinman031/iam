#!/usr/bin/env python3
"""
IAM Version Bump Script
Automates version updates across all project files.

Usage:
    python3 tools/bump_version.py rev    # 1.1.0 -> 1.1.1
    python3 tools/bump_version.py minor  # 1.1.0 -> 1.2.0
    python3 tools/bump_version.py major  # 1.1.0 -> 2.0.0

What it does:
    1. Reads current version from docs/iam_changelog.md
    2. Bumps version according to type (rev/minor/major)
    3. Updates all version headers across project
    4. Injects fresh placeholder at top of changelog
    5. Updates CURRENT ACTIVE VERSION
"""
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple


# Files that contain version strings
VERSION_FILES = [
    'docs/iam_changelog.md',
    'README.md',
    'iam_client.py',
    'app/__init__.py',
    'SETUP.md',
    'INTEGRATION_SUMMARY.md',
    'DELIVERABLES_SUMMARY.md',
]

# Current project directory
PROJECT_ROOT = Path(__file__).parent.parent


def get_current_version() -> Tuple[int, int, int]:
    """
    Read current version from changelog.
    Returns: (major, minor, revision)
    """
    changelog = PROJECT_ROOT / 'docs/iam_changelog.md'
    
    if not changelog.exists():
        print(f"❌ Error: {changelog} not found")
        sys.exit(1)
    
    content = changelog.read_text()
    
    # Look for "CURRENT ACTIVE VERSION" section
    match = re.search(r'IAM v(\d+)\.(\d+)\.(\d+)', content)
    if not match:
        print("❌ Error: Could not find version in changelog")
        sys.exit(1)
    
    major, minor, rev = map(int, match.groups())
    return major, minor, rev


def bump_version(major: int, minor: int, rev: int, bump_type: str) -> Tuple[int, int, int]:
    """
    Bump version according to type.
    Returns: (new_major, new_minor, new_rev)
    """
    if bump_type == 'rev':
        return major, minor, rev + 1
    elif bump_type == 'minor':
        return major, minor + 1, 0
    elif bump_type == 'major':
        return major + 1, 0, 0
    else:
        print(f"❌ Error: Unknown bump type '{bump_type}'. Use: rev, minor, or major")
        sys.exit(1)


def update_changelog(old_version: str, new_version: str, bump_type: str) -> None:
    """
    Update changelog with new version placeholder.
    """
    changelog = PROJECT_ROOT / 'docs/iam_changelog.md'
    content = changelog.read_text()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Generate placeholder based on bump type
    if bump_type == 'rev':
        change_type = "Bugfix / Patch"
        scope_hint = "bugfix / security / refactor"
    elif bump_type == 'minor':
        change_type = "New Feature / Enhancement"
        scope_hint = "feature / enhancement / api"
    else:  # major
        change_type = "Breaking Change / Architecture"
        scope_hint = "architecture / breaking change / migration"
    
    placeholder = f"""### 🧩 v{new_version} – {today}
**Author:** [Your Name]  
**Type:** [Insert / Edit / Remove]  
**Scope:** [{scope_hint}]  
**Summary:** [Short explanation of what changed and why]

"""
    
    # Update CURRENT ACTIVE VERSION section
    # Pattern to match: ## 🔢 CURRENT ACTIVE VERSION\n**IAM vX.Y.Z (DATE)** – DESCRIPTION
    current_version_pattern = r'(## 🔢 CURRENT ACTIVE VERSION\n\*\*IAM v)(\d+\.\d+\.\d+)( \([\d-]+\))\*\*(.*?)(\n\n---)'
    replacement = rf'\1{new_version}\3*\*\* {change_type.lower()}.\4\5'
    content = re.sub(current_version_pattern, replacement, content, flags=re.DOTALL)
    
    # Find insertion point: after "---" that follows CURRENT ACTIVE VERSION, before "## 🕒 VERSION HISTORY"
    # Split into two parts at the insertion point
    history_start = content.find('## 🕒 VERSION HISTORY')
    if history_start == -1:
        print("⚠️ Warning: Could not find '## 🕒 VERSION HISTORY' section")
        history_start = len(content)
    
    # Find the "---" marker before VERSION HISTORY
    before_history = content[:history_start]
    last_separator = before_history.rfind('---')
    
    if last_separator != -1:
        # Insert placeholder after the last "---" and before VERSION HISTORY
        new_content = (
            content[:last_separator + 3] +  # Up to and including "---"
            '\n\n' + placeholder +  # Add placeholder
            content[history_start:]  # Rest of content
        )
        content = new_content
    
    changelog.write_text(content)
    print(f"✅ Updated {changelog}")


def update_file_version(file_path: Path, old_version: str, new_version: str) -> bool:
    """
    Update version strings in a file.
    Returns: True if updated, False if not found
    """
    if not file_path.exists():
        return False
    
    content = file_path.read_text()
    original = content
    
    # Pattern 1: v1.2.3 or 1.2.3 in various contexts
    patterns = [
        (rf'\bv{re.escape(old_version)}\b', f'v{new_version}'),
        (rf'\b{re.escape(old_version)}\b', new_version),  # Fallback for bare versions
    ]
    
    # Pattern 2: Version fields in variable assignments or strings
    # e.g., "version": "1.2.3" or __version__ = "1.2.3"
    patterns.extend([
        (rf'"version": "{re.escape(old_version)}"', f'"version": "{new_version}"'),
        (rf"'version': '{re.escape(old_version)}'", f"'version': '{new_version}'"),
        (rf'__version__ = "{re.escape(old_version)}"', f'__version__ = "{new_version}"'),
        (rf'__version__ = \'{re.escape(old_version)}\'', f"__version__ = '{new_version}'"),
    ])
    
    updated = False
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            updated = True
    
    if content != original:
        file_path.write_text(content)
        print(f"✅ Updated {file_path}")
        return True
    
    return False


def main():
    """Main execution."""
    if len(sys.argv) != 2:
        print("Usage: python3 tools/bump_version.py [rev|minor|major]")
        print()
        print("Examples:")
        print("  python3 tools/bump_version.py rev    # 1.1.0 -> 1.1.1")
        print("  python3 tools/bump_version.py minor  # 1.1.0 -> 1.2.0")
        print("  python3 tools/bump_version.py major  # 1.1.0 -> 2.0.0")
        sys.exit(1)
    
    bump_type = sys.argv[1].lower()
    
    if bump_type not in ['rev', 'minor', 'major']:
        print(f"❌ Error: Unknown bump type '{bump_type}'")
        print("Use: rev, minor, or major")
        sys.exit(1)
    
    # Get current version
    major, minor, rev = get_current_version()
    old_version = f"{major}.{minor}.{rev}"
    
    # Bump version
    new_major, new_minor, new_rev = bump_version(major, minor, rev, bump_type)
    new_version = f"{new_major}.{new_minor}.{new_rev}"
    
    print(f"📦 Bumping version: {old_version} → {new_version} ({bump_type})")
    print()
    
    # Update changelog first (adds placeholder)
    update_changelog(old_version, new_version, bump_type)
    
    # Update all other files
    for relative_path in VERSION_FILES:
        file_path = PROJECT_ROOT / relative_path
        update_file_version(file_path, old_version, new_version)
    
    print()
    print("=" * 60)
    print(f"✅ Version bumped successfully: {new_version}")
    print("=" * 60)
    print()
    print("📝 Next steps:")
    print(f"   1. Fill in the changelog placeholder in docs/iam_changelog.md")
    print(f"   2. Review all changes")
    print(f"   3. Commit with message: git commit -m \"chore: bump version to {new_version}\"")
    print(f"   4. Tag release: git tag -a iam-v{new_version} -m \"IAM v{new_version}\"")
    print()


if __name__ == '__main__':
    main()
