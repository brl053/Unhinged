"""Viewport/Camera abstraction for 2D world navigation.

The viewport represents a "window" into a larger world coordinate space.
It handles:
- World-to-screen coordinate transformation
- Panning (moving the camera)
- Centering on specific world positions
- Visibility culling

Pattern: Immutable data with transformation methods that return new instances.
This allows for smooth animations by interpolating between viewport states.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Viewport:
    """Immutable viewport/camera into a 2D world.

    Attributes:
        world_x: X position of viewport's top-left corner in world coords.
        world_y: Y position of viewport's top-left corner in world coords.
        width: Viewport width in screen characters.
        height: Viewport height in screen characters.
    """

    world_x: float = 0.0
    world_y: float = 0.0
    width: int = 80
    height: int = 24

    def world_to_screen(self, wx: float, wy: float) -> tuple[int, int]:
        """Convert world coordinates to screen coordinates.

        Returns integer screen position. May be negative or beyond
        viewport bounds if the world position is outside the view.
        """
        sx = int(wx - self.world_x)
        sy = int(wy - self.world_y)
        return (sx, sy)

    def screen_to_world(self, sx: int, sy: int) -> tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        wx = sx + self.world_x
        wy = sy + self.world_y
        return (wx, wy)

    def is_visible(self, wx: float, wy: float, margin: int = 0) -> bool:
        """Check if a world position is visible in the viewport.

        Args:
            wx, wy: World coordinates to check.
            margin: Extra margin around viewport edges.
        """
        sx, sy = self.world_to_screen(wx, wy)
        return -margin <= sx < self.width + margin and -margin <= sy < self.height + margin

    def is_rect_visible(self, wx: float, wy: float, w: float, h: float) -> bool:
        """Check if any part of a world rectangle is visible."""
        # Rectangle corners in screen coords
        sx, sy = self.world_to_screen(wx, wy)
        ex, ey = sx + int(w), sy + int(h)

        # Check if rectangles overlap
        return not (ex < 0 or sx >= self.width or ey < 0 or sy >= self.height)

    def pan(self, dx: float, dy: float) -> "Viewport":
        """Return new viewport panned by delta amount."""
        return Viewport(
            world_x=self.world_x + dx,
            world_y=self.world_y + dy,
            width=self.width,
            height=self.height,
        )

    def center_on(self, wx: float, wy: float) -> "Viewport":
        """Return new viewport centered on world position."""
        return Viewport(
            world_x=wx - self.width / 2,
            world_y=wy - self.height / 2,
            width=self.width,
            height=self.height,
        )

    def with_size(self, width: int, height: int) -> "Viewport":
        """Return new viewport with different size, same center."""
        center_x = self.world_x + self.width / 2
        center_y = self.world_y + self.height / 2
        return Viewport(
            world_x=center_x - width / 2,
            world_y=center_y - height / 2,
            width=width,
            height=height,
        )

    def lerp(self, target: "Viewport", t: float) -> "Viewport":
        """Linearly interpolate between this viewport and target.

        Args:
            target: Target viewport to interpolate towards.
            t: Interpolation factor (0.0 = self, 1.0 = target).
        """
        t = max(0.0, min(1.0, t))
        return Viewport(
            world_x=self.world_x + (target.world_x - self.world_x) * t,
            world_y=self.world_y + (target.world_y - self.world_y) * t,
            width=self.width,  # Keep current size
            height=self.height,
        )

    @property
    def center(self) -> tuple[float, float]:
        """Get the world coordinates of the viewport center."""
        return (self.world_x + self.width / 2, self.world_y + self.height / 2)

    def clamp_to_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float) -> "Viewport":
        """Return viewport clamped to stay within world bounds."""
        # Calculate clamped position
        new_x = max(min_x, min(self.world_x, max_x - self.width))
        new_y = max(min_y, min(self.world_y, max_y - self.height))
        return Viewport(
            world_x=new_x,
            world_y=new_y,
            width=self.width,
            height=self.height,
        )


def create_viewport(width: int, height: int, center_x: float = 0, center_y: float = 0) -> Viewport:
    """Create a viewport centered on a world position."""
    return Viewport(
        world_x=center_x - width / 2,
        world_y=center_y - height / 2,
        width=width,
        height=height,
    )
