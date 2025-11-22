#!/usr/bin/env python3

"""
Test script for GTK4 CSS Generator
Generates CSS files from semantic tokens and outputs them for verification.
"""

import sys
from pathlib import Path

# Add the generator to path
sys.path.append(str(Path(__file__).parent))
from generators.gtk4_generator import GTK4CSSGenerator


def main():
    """Test the GTK4 CSS generator"""
    # Paths
    project_root = Path(__file__).parent.parent.parent.parent
    tokens_dir = project_root / "libs" / "design_system" / "tokens"
    output_dir = project_root / "generated" / "design_system" / "gtk4"

    print(f"Tokens directory: {tokens_dir}")
    print(f"Output directory: {output_dir}")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize generator
    generator = GTK4CSSGenerator(tokens_dir, output_dir)

    # Load tokens
    print("Loading semantic tokens...")
    generator.load_tokens()

    # Check what tokens were loaded
    print(f"Loaded token categories: {list(generator.tokens.keys())}")

    # Generate CSS
    print("Generating GTK4 CSS...")
    css_files = generator.generate_css()

    # Write CSS files
    for filename, css_content in css_files.items():
        output_path = output_dir / filename
        with open(output_path, "w") as f:
            f.write(css_content)
        print(f"Generated: {output_path}")
        print(f"  Size: {len(css_content)} characters")

    print("\nGTK4 CSS generation complete!")
    print(f"Files generated in: {output_dir}")


if __name__ == "__main__":
    main()
