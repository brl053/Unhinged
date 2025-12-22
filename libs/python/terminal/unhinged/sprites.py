"""Sprite system for text-based pixel art in the TUI.

Uses Unicode block characters to render small pixel art sprites.

Block characters used:
- █ (full block) - both pixels on
- ▀ (upper half) - top pixel on, bottom off
- ▄ (lower half) - top pixel off, bottom on
- ' ' (space) - both pixels off

Each character cell represents 2 vertical pixels.
Sprites are defined as 2D arrays where each cell is a color index.
0 = transparent, 1+ = palette colors.
"""

from dataclasses import dataclass

from libs.python.terminal.cell import Color, Style

# =============================================================================
# Sprite Data Type
# =============================================================================


@dataclass(frozen=True)
class Sprite:
    """A small pixel art sprite.

    Pixels are stored row-major. Each value is a color index (0 = transparent).
    Height should be even for clean half-block rendering.
    """

    name: str
    width: int
    height: int  # Should be even
    pixels: tuple[int, ...]  # Row-major, length = width * height
    palette: tuple[Color, ...]  # Index 0 is unused (transparent)

    def get_pixel(self, x: int, y: int) -> int:
        """Get color index at (x, y). Returns 0 if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.pixels[y * self.width + x]
        return 0


# =============================================================================
# Sprite Renderer
# =============================================================================


def render_sprite(sprite: Sprite, x: int, y: int, put_char) -> None:
    """Render a sprite at position (x, y) using half-block characters.

    Args:
        sprite: The sprite to render.
        x, y: Top-left position in screen coordinates.
        put_char: Function(x, y, char, style) to draw a character.
    """
    # Process two rows at a time (top and bottom pixels per cell)
    for row_pair in range(0, sprite.height, 2):
        for col in range(sprite.width):
            top_idx = sprite.get_pixel(col, row_pair)
            bot_idx = sprite.get_pixel(col, row_pair + 1) if row_pair + 1 < sprite.height else 0

            if top_idx == 0 and bot_idx == 0:
                # Both transparent - skip
                continue

            # Determine character and colors
            if top_idx != 0 and bot_idx != 0:
                if top_idx == bot_idx:
                    # Same color - full block
                    char = "█"
                    style = Style(fg=sprite.palette[top_idx - 1])
                else:
                    # Different colors - use ▀ with fg=top, bg=bottom
                    char = "▀"
                    style = Style(fg=sprite.palette[top_idx - 1], bg=sprite.palette[bot_idx - 1])
            elif top_idx != 0:
                # Only top - upper half block
                char = "▀"
                style = Style(fg=sprite.palette[top_idx - 1])
            else:
                # Only bottom - lower half block
                char = "▄"
                style = Style(fg=sprite.palette[bot_idx - 1])

            put_char(x + col, y + row_pair // 2, char, style)


# =============================================================================
# Sprite Definitions for Node Types
# =============================================================================

# Color palettes
PALETTE_BLUE = (Color.BLUE, Color.CYAN, Color.WHITE)
PALETTE_GREEN = (Color.GREEN, Color.BRIGHT_GREEN, Color.WHITE)
PALETTE_RED = (Color.RED, Color.YELLOW, Color.WHITE)
PALETTE_PURPLE = (Color.MAGENTA, Color.BRIGHT_MAGENTA, Color.WHITE)
PALETTE_YELLOW = (Color.YELLOW, Color.BRIGHT_YELLOW, Color.WHITE)
PALETTE_GRAY = (Color.BRIGHT_BLACK, Color.WHITE, Color.CYAN)

# 4x4 pixel sprites (renders as 4x2 characters)
# Each row is 4 pixels, 4 rows total
# 0 = transparent, 1 = primary color, 2 = secondary, 3 = accent

# LLM/AI node - brain/thought bubble shape
SPRITE_LLM = Sprite(
    name="llm",
    width=4,
    height=4,
    pixels=(
        0,
        1,
        1,
        0,
        1,
        3,
        3,
        1,
        1,
        2,
        2,
        1,
        0,
        1,
        0,
        0,
    ),
    palette=PALETTE_BLUE,
)

# Transform/Process node - gear/cog shape
SPRITE_TRANSFORM = Sprite(
    name="transform",
    width=4,
    height=4,
    pixels=(
        1,
        0,
        0,
        1,
        0,
        2,
        2,
        0,
        0,
        2,
        2,
        0,
        1,
        0,
        0,
        1,
    ),
    palette=PALETTE_GREEN,
)

# HTTP/Network node - globe/world shape
SPRITE_HTTP = Sprite(
    name="http",
    width=4,
    height=4,
    pixels=(
        0,
        1,
        1,
        0,
        1,
        2,
        2,
        1,
        1,
        1,
        1,
        1,
        0,
        1,
        1,
        0,
    ),
    palette=PALETTE_YELLOW,
)

# Conditional/Branch node - diamond decision
SPRITE_CONDITION = Sprite(
    name="condition",
    width=4,
    height=4,
    pixels=(
        0,
        0,
        1,
        0,
        0,
        1,
        2,
        1,
        0,
        1,
        2,
        1,
        0,
        0,
        1,
        0,
    ),
    palette=PALETTE_RED,
)

# Default/Unknown node - question mark box
SPRITE_DEFAULT = Sprite(
    name="default",
    width=4,
    height=4,
    pixels=(
        1,
        1,
        1,
        1,
        1,
        0,
        2,
        1,
        1,
        0,
        0,
        1,
        1,
        1,
        2,
        1,
    ),
    palette=PALETTE_GRAY,
)

# Unix/Shell command node - terminal prompt >_
SPRITE_UNIX = Sprite(
    name="unix",
    width=4,
    height=4,
    pixels=(
        1,
        1,
        1,
        1,
        1,
        2,
        0,
        1,
        1,
        2,
        2,
        1,
        1,
        1,
        1,
        1,
    ),
    palette=PALETTE_GREEN,
)

# Speech-to-text node - microphone shape
SPRITE_INPUT = Sprite(
    name="input",
    width=4,
    height=4,
    pixels=(
        0,
        1,
        1,
        0,
        0,
        1,
        1,
        0,
        0,
        2,
        2,
        0,
        0,
        0,
        1,
        0,
    ),
    palette=PALETTE_BLUE,
)

# Text-to-speech node - speaker shape
SPRITE_OUTPUT = Sprite(
    name="output",
    width=4,
    height=4,
    pixels=(
        0,
        1,
        0,
        0,
        0,
        1,
        1,
        2,
        0,
        1,
        1,
        2,
        0,
        1,
        0,
        0,
    ),
    palette=PALETTE_PURPLE,
)


# =============================================================================
# Sprite Registry
# =============================================================================

from libs.python.models.graph.schema import NodeType

# Map node types to sprites
NODE_TYPE_SPRITES: dict[NodeType, Sprite] = {
    NodeType.LLM_CHAT: SPRITE_LLM,
    NodeType.LLM_COMPLETION: SPRITE_LLM,
    NodeType.VISION_AI: SPRITE_LLM,
    NodeType.IMAGE_GENERATION: SPRITE_LLM,
    NodeType.DATA_TRANSFORM: SPRITE_TRANSFORM,
    NodeType.CONTEXT_HYDRATION: SPRITE_TRANSFORM,
    NodeType.PROMPT_ENHANCEMENT: SPRITE_TRANSFORM,
    NodeType.HTTP_REQUEST: SPRITE_HTTP,
    NodeType.CONDITIONAL: SPRITE_CONDITION,
    NodeType.LOOP_BREAKER: SPRITE_CONDITION,
    NodeType.CUSTOM_SERVICE: SPRITE_UNIX,
    NodeType.SPEECH_TO_TEXT: SPRITE_INPUT,
    NodeType.TEXT_TO_SPEECH: SPRITE_OUTPUT,
}


def get_sprite_for_node_type(node_type: NodeType) -> Sprite:
    """Get the sprite for a node type."""
    return NODE_TYPE_SPRITES.get(node_type, SPRITE_DEFAULT)


def render_sprite_to_renderer(sprite: Sprite, x: int, y: int, renderer) -> None:
    """Render a sprite using a Renderer instance.

    Args:
        sprite: The sprite to render.
        x, y: Top-left position.
        renderer: A Renderer instance with a text() method.
    """

    def put_char(px: int, py: int, char: str, style: Style):
        renderer.text(px, py, char, style)

    render_sprite(sprite, x, y, put_char)
