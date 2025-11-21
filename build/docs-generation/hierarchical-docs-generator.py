#!/usr/bin/env python3
"""
@llm-does Hierarchical documentation generator that creates organized markdown files from LlmDocs comments by @llm-type hierarchy
@llm-type build.generator/hierarchical-docs
@llm-context Homogeneous documentation architecture generator that transforms LlmDocs extracted comments into systematically organized markdown files. Processes extracted-comments.json and groups content by hierarchical @llm-type categories (architecture.system, build.orchestrator, service.api, etc.) to generate domain-specific documentation files. Replaces heterogeneous documentation generation with single unified approach where all docs come from LlmDocs with consistent depth and organization. Output structure: docs/architecture/ (system design, components), docs/build/ (orchestration, profiles), docs/services/ (API, voice, graphics), docs/development/ (workflow, testing). Each generated file contains rich contextual information from @llm-context tags, organized by hierarchical classification, with consistent markdown formatting and cross-references.
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


class HierarchicalDocsGenerator:
    """Generates organized documentation from LlmDocs hierarchical types"""

    def __init__(self, root_path: str = None):
        if root_path is None:
            # Auto-detect project root by looking for docs directory
            current = Path(__file__).resolve().parent
            while current != current.parent:
                if (current / "docs").exists():
                    root_path = current
                    break
                current = current.parent
            else:
                root_path = Path(".").resolve()

        self.root_path = Path(root_path).resolve()
        self.docs_dir = self.root_path / "docs"
        self.extracted_comments_path = self.docs_dir / "architecture" / "extracted-comments.json"

        print(f"🔍 Root path: {self.root_path}")
        print(f"🔍 Docs dir: {self.docs_dir}")
        print(f"🔍 Extracted comments path: {self.extracted_comments_path}")

    def generate_hierarchical_docs(self) -> bool:
        """Generate organized documentation from LlmDocs extraction"""
        print("🏗️ Generating hierarchical documentation from LlmDocs...")

        try:
            # Load extracted comments
            if not self.extracted_comments_path.exists():
                print(f"❌ Extracted comments not found: {self.extracted_comments_path}")
                return False

            with open(self.extracted_comments_path) as f:
                data = json.load(f)

            # Handle both list format and dict format
            if isinstance(data, list):
                comments = data
            else:
                comments = data.get("comments", [])

            if not comments:
                print("⚠️ No comments found in extraction data")
                return True

            print(f"📊 Processing {len(comments)} comments...")

            # Group comments by hierarchical type
            grouped_comments = self._group_by_hierarchy(comments)
            print(f"📊 Grouped into {len(grouped_comments)} categories")

            # Generate documentation files
            generated_files = []
            for category, subcategories in grouped_comments.items():
                print(f"📁 Processing category: {category}")
                for subcategory, comment_list in subcategories.items():
                    print(
                        f"  📄 Processing subcategory: {subcategory} ({len(comment_list) if comment_list else 0} comments)"
                    )
                    try:
                        file_path = self._generate_category_docs(category, subcategory, comment_list)
                        if file_path:
                            generated_files.append(file_path)
                    except Exception as e:
                        print(f"❌ Error generating docs for {category}.{subcategory}: {e}")
                        raise

            # Generate index files
            self._generate_category_indexes(grouped_comments)

            print(f"✅ Generated {len(generated_files)} hierarchical documentation files")
            return True

        except Exception as e:
            print(f"❌ Error generating hierarchical docs: {e}")
            return False

    def _group_by_hierarchy(self, comments: list[dict[str, Any]]) -> dict[str, dict[str, list[dict]]]:
        """Group comments by hierarchical @llm-type categories"""
        grouped = defaultdict(lambda: defaultdict(list))

        for comment in comments:
            llm_type = comment.get("llm_type")
            if not llm_type:
                continue

            # Parse hierarchical type (e.g., "build.orchestrator/unhinged-os-builder")
            if "." in llm_type:
                parts = llm_type.split(".")
                category = parts[0]  # e.g., "build"
                subcategory = parts[1].split("/")[0] if "/" in parts[1] else parts[1]  # e.g., "orchestrator"

                grouped[category][subcategory].append(comment)
            else:
                # Handle non-hierarchical types
                grouped["misc"]["general"].append(comment)

        return dict(grouped)

    def _generate_category_docs(self, category: str, subcategory: str, comments: list[dict]) -> Path:
        """Generate documentation file for a specific category/subcategory"""

        # Create category directory
        category_dir = self.docs_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = f"{subcategory}.md"
        file_path = category_dir / filename

        # Generate content
        with open(file_path, "w") as f:
            # Header
            f.write(f"# {category.title()} - {subcategory.title()}\n\n")
            f.write(f"> **Generated from LlmDocs**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"> **Category**: `{category}.{subcategory}`\n")
            f.write(f"> **Components**: {len(comments)}\n\n")

            # Table of contents
            f.write("## Components\n\n")
            for i, comment in enumerate(comments, 1):
                element_name = comment.get("element_name", "Unknown") if comment else "Unknown"
                file_path_rel = comment.get("file_path", "") if comment else ""
                if file_path_rel:
                    file_path_rel = file_path_rel.replace(str(self.root_path) + "/", "")
                f.write(f"{i}. [{element_name}](#{self._make_anchor(element_name)}) - `{file_path_rel}`\n")
            f.write("\n")

            # Detailed sections
            for comment in comments:
                if comment:  # Skip None comments
                    self._write_comment_section(f, comment)

        return file_path

    def _write_comment_section(self, f, comment: dict[str, Any]):
        """Write a detailed section for a single comment"""
        element_name = comment.get("element_name", "Unknown")
        file_path = comment.get("file_path", "").replace(str(self.root_path) + "/", "")
        llm_does = comment.get("llm_does", "")
        llm_context = comment.get("llm_context", "")
        llm_rule = comment.get("llm_rule", "")
        language = comment.get("language", "")

        # Section header
        f.write(f"## {element_name}\n\n")

        # Metadata
        f.write("### Metadata\n\n")
        f.write(f"- **File**: `{file_path}`\n")
        f.write(f"- **Language**: {language}\n")
        f.write(f"- **Type**: `{comment.get('llm_type', '')}`\n\n")

        # Purpose
        if llm_does:
            f.write("### Purpose\n\n")
            f.write(f"{llm_does}\n\n")

        # Context
        if llm_context:
            f.write("### Context\n\n")
            # Format long context for readability
            context_formatted = self._format_context(llm_context)
            f.write(f"{context_formatted}\n\n")

        # Rules/Constraints
        if llm_rule:
            f.write("### Rules & Constraints\n\n")
            f.write(f"⚠️ **Critical**: {llm_rule}\n\n")

        f.write("---\n\n")

    def _format_context(self, context: str) -> str:
        """Format long context text for better readability"""
        if len(context) < 200:
            return context

        # Break long context into paragraphs at sentence boundaries
        sentences = context.split(". ")
        paragraphs = []
        current_paragraph = []
        current_length = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Add period back if it was removed by split
            if not sentence.endswith(".") and not sentence.endswith(":") and not sentence.endswith(")"):
                sentence += "."

            current_paragraph.append(sentence)
            current_length += len(sentence)

            # Break paragraph if it gets too long
            if current_length > 300:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
                current_length = 0

        # Add remaining sentences
        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        return "\n\n".join(paragraphs)

    def _make_anchor(self, text: str) -> str:
        """Convert text to markdown anchor"""
        return text.lower().replace(" ", "-").replace("_", "-")

    def _generate_category_indexes(self, grouped_comments: dict[str, dict[str, list[dict]]]):
        """Generate index files for each category"""

        for category, subcategories in grouped_comments.items():
            category_dir = self.docs_dir / category
            index_path = category_dir / "README.md"

            with open(index_path, "w") as f:
                f.write(f"# {category.title()} Documentation\n\n")
                f.write(f"> **Generated from LlmDocs**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"> **Category**: `{category}.*`\n\n")

                f.write("## Subcategories\n\n")

                for subcategory, comments in subcategories.items():
                    f.write(f"### [{subcategory.title()}]({subcategory}.md)\n\n")

                    if comments:
                        f.write(f"**Components**: {len(comments)}\n\n")

                        # List first few components
                        for comment in comments[:3]:
                            if comment:
                                element_name = comment.get("element_name", "Unknown")
                                llm_does = comment.get("llm_does", "")
                                if llm_does and len(llm_does) > 100:
                                    llm_does = llm_does[:100] + "..."
                                f.write(f"- **{element_name}**: {llm_does}\n")

                        if len(comments) > 3:
                            f.write(f"- *...and {len(comments) - 3} more*\n")
                    else:
                        f.write("**Components**: 0\n\n")

                    f.write("\n")


def main():
    """Main entry point"""
    # Determine project root - go up from script location to find docs directory
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent  # build/docs-generation -> build -> project_root

    generator = HierarchicalDocsGenerator(str(project_root))
    success = generator.generate_hierarchical_docs()

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
