import argparse
import os
import sys
import logging
from typing import List, Optional

from yaml2cypher.converter import YAML2Cypher


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Optional list of command line arguments

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Convert YAML files to Cypher queries"
    )
    parser.add_argument("yaml_file", help="Path to YAML file")
    parser.add_argument(
        "-o", "--output", help="Output Cypher file (default: <input>.cypher)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    return parser.parse_args(args)


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the command-line interface.

    Args:
        args: Optional list of command line arguments

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parsed_args = parse_args(args)

    # Configure logging based on verbosity
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    # Determine output filename if not specified
    if not parsed_args.output:
        base_name = os.path.splitext(parsed_args.yaml_file)[0]
        parsed_args.output = f"{base_name}.cypher"

    try:
        converter = YAML2Cypher()
        cypher_statements = converter.yaml_file_to_cypher(
            parsed_args.yaml_file
        )
        converter.write_cypher_to_file(cypher_statements, parsed_args.output)
        print(f"Converted {parsed_args.yaml_file} to {parsed_args.output}")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
