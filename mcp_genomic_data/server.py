"""MCP Server for Genomic Data Access - Integrated with ARCHCODE."""

import json
import sys
from typing import Any

try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import (
        TextContent,
        Tool,
    )
except ImportError:
    print("MCP SDK not installed. Install with: pip install mcp")
    sys.exit(1)

from mcp_genomic_data.tools import (
    calculate_insulation_score,
    classify_te_family,
    detect_tads_from_hic,
    fetch_ctcf_chipseq,
    fetch_genomic_sequence,
    fetch_hic_data,
    fetch_methylation_data,
    fetch_te_annotations,
    search_gene,
)

# Initialize MCP Server
app = Server("genomic-data-mcp")

# Register tools
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available genomic data tools."""
    return [
        Tool(
            name="fetch_genomic_sequence",
            description="Fetch genomic sequence from UCSC/Ensembl",
            inputSchema={
                "type": "object",
                "properties": {
                    "chromosome": {"type": "string", "description": "Chromosome (e.g., 'chr1')"},
                    "start": {"type": "integer", "description": "Start position (bp)"},
                    "end": {"type": "integer", "description": "End position (bp)"},
                    "assembly": {"type": "string", "description": "Genome assembly (default: hg38)"},
                },
                "required": ["chromosome", "start", "end"],
            },
        ),
        Tool(
            name="fetch_ctcf_chipseq",
            description="Fetch CTCF ChIP-seq data from ENCODE",
            inputSchema={
                "type": "object",
                "properties": {
                    "chromosome": {"type": "string"},
                    "start": {"type": "integer"},
                    "end": {"type": "integer"},
                    "cell_type": {"type": "string", "description": "Cell type (optional)"},
                },
                "required": ["chromosome", "start", "end"],
            },
        ),
        Tool(
            name="fetch_hic_data",
            description="Fetch Hi-C contact data",
            inputSchema={
                "type": "object",
                "properties": {
                    "chromosome": {"type": "string"},
                    "resolution": {"type": "integer", "description": "Resolution in bp (e.g., 10000)"},
                    "file_path": {"type": "string", "description": "Path to .cool/.mcool file"},
                },
                "required": ["chromosome", "resolution"],
            },
        ),
        Tool(
            name="fetch_methylation_data",
            description="Fetch CpG methylation data",
            inputSchema={
                "type": "object",
                "properties": {
                    "chromosome": {"type": "string"},
                    "start": {"type": "integer"},
                    "end": {"type": "integer"},
                    "data_source": {"type": "string", "description": "Data source (GEO, ENCODE)"},
                },
                "required": ["chromosome", "start", "end"],
            },
        ),
        Tool(
            name="search_gene",
            description="Search for gene and get coordinates",
            inputSchema={
                "type": "object",
                "properties": {
                    "gene_name": {"type": "string", "description": "Gene name or symbol"},
                    "assembly": {"type": "string", "description": "Genome assembly (default: hg38)"},
                },
                "required": ["gene_name"],
            },
        ),
        Tool(
            name="fetch_te_annotations",
            description="Fetch transposon element annotations",
            inputSchema={
                "type": "object",
                "properties": {
                    "chromosome": {"type": "string"},
                    "start": {"type": "integer"},
                    "end": {"type": "integer"},
                    "annotation_source": {"type": "string", "description": "RepeatMasker, Dfam"},
                },
                "required": ["chromosome", "start", "end"],
            },
        ),
        Tool(
            name="classify_te_family",
            description="Classify TE family from sequence",
            inputSchema={
                "type": "object",
                "properties": {
                    "sequence": {"type": "string", "description": "DNA sequence"},
                },
                "required": ["sequence"],
            },
        ),
        Tool(
            name="calculate_insulation_score",
            description="Calculate insulation score from Hi-C data",
            inputSchema={
                "type": "object",
                "properties": {
                    "chromosome": {"type": "string"},
                    "file_path": {"type": "string", "description": "Path to .cool file"},
                    "window_size": {"type": "integer", "description": "Window size in bp"},
                },
                "required": ["chromosome", "file_path"],
            },
        ),
        Tool(
            name="detect_tads_from_hic",
            description="Detect TAD boundaries from Hi-C data",
            inputSchema={
                "type": "object",
                "properties": {
                    "chromosome": {"type": "string"},
                    "file_path": {"type": "string"},
                    "resolution": {"type": "integer"},
                },
                "required": ["chromosome", "file_path"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Execute genomic data tool."""
    try:
        if name == "fetch_genomic_sequence":
            result = await fetch_genomic_sequence(
                arguments["chromosome"],
                arguments["start"],
                arguments["end"],
                arguments.get("assembly", "hg38"),
            )
        elif name == "fetch_ctcf_chipseq":
            result = await fetch_ctcf_chipseq(
                arguments["chromosome"],
                arguments["start"],
                arguments["end"],
                arguments.get("cell_type"),
            )
        elif name == "fetch_hic_data":
            result = await fetch_hic_data(
                arguments["chromosome"],
                arguments["resolution"],
                arguments.get("file_path"),
            )
        elif name == "fetch_methylation_data":
            result = await fetch_methylation_data(
                arguments["chromosome"],
                arguments["start"],
                arguments["end"],
                arguments.get("data_source", "ENCODE"),
            )
        elif name == "search_gene":
            result = await search_gene(
                arguments["gene_name"],
                arguments.get("assembly", "hg38"),
            )
        elif name == "fetch_te_annotations":
            result = await fetch_te_annotations(
                arguments["chromosome"],
                arguments["start"],
                arguments["end"],
                arguments.get("annotation_source", "RepeatMasker"),
            )
        elif name == "classify_te_family":
            result = await classify_te_family(arguments["sequence"])
        elif name == "calculate_insulation_score":
            result = await calculate_insulation_score(
                arguments["chromosome"],
                arguments["file_path"],
                arguments.get("window_size", 500000),
            )
        elif name == "detect_tads_from_hic":
            result = await detect_tads_from_hic(
                arguments["chromosome"],
                arguments["file_path"],
                arguments.get("resolution", 10000),
            )
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error executing {name}: {str(e)}",
            )
        ]


async def main() -> None:
    """Main entry point for MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="genomic-data-mcp",
                server_version="1.0.0-alpha",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

