import subprocess
import sys

# Option 1: Try pypandoc (Python wrapper for Pandoc)
try:
    import pypandoc
    output = pypandoc.convert_file(
        'manuscript_v2_full.md',
        'docx',
        outputfile='manuscript_v2_bioRxiv.docx',
        extra_args=['--reference-doc=template.docx'] if Path('template.docx').exists() else []
    )
    print("✓ Converted via pypandoc")
    sys.exit(0)
except ImportError:
    pass

# Option 2: Direct pandoc call
try:
    result = subprocess.run(
        ['pandoc', 'manuscript_v2_full.md', '-o', 'manuscript_v2_bioRxiv.docx',
         '--standalone'],
        capture_output=True, text=True, check=True
    )
    print("✓ Converted via pandoc CLI")
    print(f"  Output: {result.stdout}")
    sys.exit(0)
except (subprocess.CalledProcessError, FileNotFoundError) as e:
    print(f"✗ Pandoc failed: {e}")
    sys.exit(1)
