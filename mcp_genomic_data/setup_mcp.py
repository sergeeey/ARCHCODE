"""Setup script for MCP Genomic Data Server."""

import json
import sys
from pathlib import Path


def create_mcp_config() -> None:
    """Create MCP server configuration for Cursor."""
    # Cursor MCP configuration location
    config_dir = Path.home() / ".cursor" / "mcp"
    config_dir.mkdir(parents=True, exist_ok=True)

    config_file = config_dir / "genomic-data.json"

    config = {
        "mcpServers": {
            "genomic-data": {
                "command": "python",
                "args": [
                    str(Path(__file__).parent / "server.py"),
                ],
                "env": {
                    "PYTHONPATH": str(Path(__file__).parent.parent),
                },
            }
        }
    }

    # Check if config already exists
    if config_file.exists():
        print(f"⚠️  Config file already exists: {config_file}")
        response = input("Overwrite? (y/n): ")
        if response.lower() != "y":
            print("Skipping config creation")
            return

    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    print(f"✅ MCP config created: {config_file}")
    print("\nTo use in Cursor:")
    print("1. Restart Cursor")
    print("2. MCP server 'genomic-data' will be available")


def main() -> None:
    """Main setup function."""
    print("=" * 60)
    print("MCP Genomic Data Server Setup")
    print("=" * 60)

    # Check dependencies
    print("\nChecking dependencies...")
    try:
        import mcp  # noqa: F401
        print("✅ mcp installed")
    except ImportError:
        print("❌ mcp not installed")
        print("   Install with: pip install mcp")
        sys.exit(1)

    try:
        import Bio  # noqa: F401
        print("✅ biopython installed")
    except ImportError:
        print("⚠️  biopython not installed (optional)")

    try:
        import cooler  # noqa: F401
        print("✅ cooler installed")
    except ImportError:
        print("⚠️  cooler not installed (optional for Hi-C)")

    # Create config
    print("\nCreating MCP configuration...")
    create_mcp_config()

    print("\n" + "=" * 60)
    print("✅ Setup Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()

