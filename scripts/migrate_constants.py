#!/usr/bin/env python3
"""
Script to migrate magic strings to constants
Run: python scripts/migrate_constants.py
"""

import re
from pathlib import Path

REPLACEMENTS = {
    r'"guardada"': 'OrderState.GUARDADA.value',
    r'"registrada"': 'OrderState.REGISTRADA.value',
    r'"GENERAL"': 'SectionNames.GENERAL',
}

def migrate_file(file_path: Path):
    """Migrate a single file"""
    content = file_path.read_text(encoding='utf-8')
    original = content

    for pattern, replacement in REPLACEMENTS.items():
        content = re.sub(pattern, replacement, content)

    if content != original:
        # Add import at top
        if 'from src.modules.receipts.constants import' not in content:
            lines = content.split('\n')
            # Find last import line
            last_import = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    last_import = i

            lines.insert(last_import + 1,
                        'from src.modules.receipts.constants import OrderState, SectionNames')
            content = '\n'.join(lines)

        file_path.write_text(content, encoding='utf-8')
        print(f"✅ Migrated: {file_path}")

def main():
    receipts_dir = Path('src/modules/receipts')
    py_files = receipts_dir.rglob('*.py')

    migrated_count = 0
    for py_file in py_files:
        if 'constants.py' not in str(py_file):
            try:
                migrate_file(py_file)
                migrated_count += 1
            except Exception as e:
                print(f"❌ Error migrating {py_file}: {e}")

    print(f"\n🎉 Migration complete! Processed {migrated_count} files.")

if __name__ == '__main__':
    main()
