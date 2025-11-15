#!/usr/bin/env python3
"""
CFFI build script for Unhinged Graphics Library

Generates Python bindings for the C graphics library using CFFI.
This allows the Python layout engine to call C graphics functions directly
for maximum performance.
"""

import os
from pathlib import Path

from cffi import FFI

# Configuration from CMake
LIBRARY_NAME = "unhinged_graphics"
INSTALL_PREFIX = "/home/e-bliss-station-1/Projects/Unhinged/generated/c/graphics"
BUILD_DIR = "/home/e-bliss-station-1/Projects/Unhinged/libs/graphics/build"
SOURCE_DIR = "/home/e-bliss-station-1/Projects/Unhinged/libs/graphics"


def build_cffi_bindings():
    """Build CFFI bindings for the graphics library"""

    ffibuilder = FFI()

    # Define the C interface
    ffibuilder.cdef(
        """
        // Version and initialization
        const char* ug_get_version(void);
        int ug_init(void);
        void ug_shutdown(void);

        // Error codes
        typedef enum {
            UG_SUCCESS = 0,
            UG_ERROR_INVALID_PARAM = -1,
            UG_ERROR_OUT_OF_MEMORY = -2,
            UG_ERROR_PLATFORM_NOT_SUPPORTED = -3,
            UG_ERROR_SIMD_NOT_AVAILABLE = -4,
            UG_ERROR_INITIALIZATION_FAILED = -5
        } ug_error_t;

        // Basic types
        typedef struct {
            int32_t x, y;
        } ug_point_t;

        typedef struct {
            int32_t x, y, width, height;
        } ug_rect_t;

        typedef struct {
            uint8_t r, g, b, a;
        } ug_color_t;

        typedef struct {
            float r, g, b, a;
        } ug_color_f_t;

        // Surface structure (opaque)
        typedef struct ug_surface ug_surface_t;
        typedef struct ug_allocator ug_allocator_t;

        // Platform capabilities
        typedef struct {
            bool has_avx2;
            bool has_neon;
            bool has_drm;
            bool has_wayland;
            const char *gpu_vendor;
            const char *platform_name;
        } ug_platform_caps_t;

        // Blend modes
        typedef enum {
            UG_BLEND_NONE = 0,
            UG_BLEND_ALPHA,
            UG_BLEND_ADD,
            UG_BLEND_MULTIPLY,
            UG_BLEND_SCREEN
        } ug_blend_mode_t;

        // Color spaces
        typedef enum {
            UG_COLOR_SPACE_RGB = 0,
            UG_COLOR_SPACE_HSV,
            UG_COLOR_SPACE_HSL,
            UG_COLOR_SPACE_LAB
        } ug_color_space_t;

        // Core API
        ug_platform_caps_t ug_get_platform_caps(void);

        // Memory management
        ug_allocator_t* ug_allocator_create(size_t pool_size);
        void ug_allocator_destroy(ug_allocator_t* allocator);
        void* ug_allocator_alloc(ug_allocator_t* allocator, size_t size, size_t alignment);
        void ug_allocator_free(ug_allocator_t* allocator, void* ptr);

        // Surface management
        ug_surface_t* ug_surface_create(int32_t width, int32_t height, ug_allocator_t* allocator);
        void ug_surface_destroy(ug_surface_t* surface);
        ug_error_t ug_surface_clear(ug_surface_t* surface, ug_color_t color);

        // Drawing primitives
        ug_error_t ug_draw_line(ug_surface_t* surface, int32_t x0, int32_t y0,
                               int32_t x1, int32_t y1, ug_color_t color);
        ug_error_t ug_draw_circle_filled(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                        int32_t radius, ug_color_t color);
        ug_error_t ug_draw_circle_outline(ug_surface_t* surface, int32_t center_x, int32_t center_y,
                                         int32_t radius, ug_color_t color);
        ug_error_t ug_draw_rect_filled(ug_surface_t* surface, ug_rect_t rect, ug_color_t color);

        // Color operations
        ug_color_f_t ug_color_convert(ug_color_f_t src_color, ug_color_space_t src_space,
                                     ug_color_space_t dst_space);
        ug_color_t ug_color_blend(ug_color_t src, ug_color_t dst, ug_blend_mode_t mode);
        ug_color_t ug_color_alpha_blend(ug_color_t src, ug_color_t dst);

        // Utility functions
        ug_color_f_t ug_color_u8_to_float(ug_color_t color);
        ug_color_t ug_color_float_to_u8(ug_color_f_t color);
    """
    )

    # Set the source
    library_path = os.path.join(INSTALL_PREFIX, "lib", f"lib{LIBRARY_NAME}.so")
    if not os.path.exists(library_path):
        # Try build directory
        library_path = os.path.join(BUILD_DIR, f"lib{LIBRARY_NAME}.so")

    ffibuilder.set_source(
        "_unhinged_graphics",
        """
        #include "unhinged_graphics.h"
        """,
        libraries=[LIBRARY_NAME],
        library_dirs=[os.path.join(INSTALL_PREFIX, "lib"), BUILD_DIR],
        include_dirs=[os.path.join(INSTALL_PREFIX, "include"), os.path.join(SOURCE_DIR, "include")],
    )

    return ffibuilder


def create_python_wrapper():
    """Create high-level Python wrapper"""

    wrapper_code = '''
"""
Unhinged Graphics Library - Python Bindings

High-performance graphics rendering library with Python integration.
Provides 2D rasterization, color operations, and SIMD acceleration.
"""

import numpy as np
from _unhinged_graphics import ffi, lib

class GraphicsError(Exception):
    """Graphics library error"""
    pass

class Color:
    """Color representation with conversion utilities"""

    def __init__(self, r=0, g=0, b=0, a=255):
        self.r = max(0, min(255, int(r)))
        self.g = max(0, min(255, int(g)))
        self.b = max(0, min(255, int(b)))
        self.a = max(0, min(255, int(a)))

    def to_c_color(self):
        """Convert to C color structure"""
        return ffi.new("ug_color_t *", {
            "r": self.r, "g": self.g, "b": self.b, "a": self.a
        })[0]

    @classmethod
    def from_c_color(cls, c_color):
        """Create Color from C color structure"""
        return cls(c_color.r, c_color.g, c_color.b, c_color.a)

    def to_hex(self):
        """Convert to hex string"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}{self.a:02x}"

    @classmethod
    def from_hex(cls, hex_str):
        """Create Color from hex string"""
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            hex_str += 'ff'  # Add alpha
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        a = int(hex_str[6:8], 16)
        return cls(r, g, b, a)

class Surface:
    """Graphics surface for rendering"""

    def __init__(self, width, height, allocator=None):
        self.width = width
        self.height = height
        self._surface = lib.ug_surface_create(width, height, allocator)
        if self._surface == ffi.NULL:
            raise GraphicsError("Failed to create surface")

    def __del__(self):
        if hasattr(self, '_surface') and self._surface != ffi.NULL:
            lib.ug_surface_destroy(self._surface)

    def clear(self, color):
        """Clear surface with solid color"""
        if isinstance(color, Color):
            c_color = color.to_c_color()
        else:
            c_color = color

        result = lib.ug_surface_clear(self._surface, c_color)
        if result != lib.UG_SUCCESS:
            raise GraphicsError(f"Failed to clear surface: {result}")

    def draw_line(self, x0, y0, x1, y1, color):
        """Draw line between two points"""
        if isinstance(color, Color):
            c_color = color.to_c_color()
        else:
            c_color = color

        result = lib.ug_draw_line(self._surface, x0, y0, x1, y1, c_color)
        if result != lib.UG_SUCCESS:
            raise GraphicsError(f"Failed to draw line: {result}")

    def draw_circle_filled(self, center_x, center_y, radius, color):
        """Draw filled circle"""
        if isinstance(color, Color):
            c_color = color.to_c_color()
        else:
            c_color = color

        result = lib.ug_draw_circle_filled(self._surface, center_x, center_y, radius, c_color)
        if result != lib.UG_SUCCESS:
            raise GraphicsError(f"Failed to draw filled circle: {result}")

    def draw_circle_outline(self, center_x, center_y, radius, color):
        """Draw circle outline"""
        if isinstance(color, Color):
            c_color = color.to_c_color()
        else:
            c_color = color

        result = lib.ug_draw_circle_outline(self._surface, center_x, center_y, radius, c_color)
        if result != lib.UG_SUCCESS:
            raise GraphicsError(f"Failed to draw circle outline: {result}")

    def draw_rect_filled(self, x, y, width, height, color):
        """Draw filled rectangle"""
        if isinstance(color, Color):
            c_color = color.to_c_color()
        else:
            c_color = color

        rect = ffi.new("ug_rect_t *", {"x": x, "y": y, "width": width, "height": height})[0]
        result = lib.ug_draw_rect_filled(self._surface, rect, c_color)
        if result != lib.UG_SUCCESS:
            raise GraphicsError(f"Failed to draw filled rectangle: {result}")

class Graphics:
    """Main graphics library interface"""

    def __init__(self):
        result = lib.ug_init()
        if result != lib.UG_SUCCESS:
            raise GraphicsError(f"Failed to initialize graphics library: {result}")

        self._initialized = True

    def __del__(self):
        if hasattr(self, '_initialized') and self._initialized:
            lib.ug_shutdown()

    @property
    def version(self):
        """Get library version"""
        return ffi.string(lib.ug_get_version()).decode('utf-8')

    @property
    def platform_caps(self):
        """Get platform capabilities"""
        caps = lib.ug_get_platform_caps()
        return {
            'has_avx2': caps.has_avx2,
            'has_neon': caps.has_neon,
            'has_drm': caps.has_drm,
            'has_wayland': caps.has_wayland,
            'gpu_vendor': ffi.string(caps.gpu_vendor).decode('utf-8'),
            'platform_name': ffi.string(caps.platform_name).decode('utf-8')
        }

    def create_surface(self, width, height):
        """Create a new rendering surface"""
        return Surface(width, height)

    def blend_colors(self, src_color, dst_color, blend_mode='alpha'):
        """Blend two colors"""
        blend_modes = {
            'none': lib.UG_BLEND_NONE,
            'alpha': lib.UG_BLEND_ALPHA,
            'add': lib.UG_BLEND_ADD,
            'multiply': lib.UG_BLEND_MULTIPLY,
            'screen': lib.UG_BLEND_SCREEN
        }

        if isinstance(src_color, Color):
            src_c = src_color.to_c_color()
        else:
            src_c = src_color

        if isinstance(dst_color, Color):
            dst_c = dst_color.to_c_color()
        else:
            dst_c = dst_color

        mode = blend_modes.get(blend_mode, lib.UG_BLEND_ALPHA)
        result = lib.ug_color_blend(src_c, dst_c, mode)

        return Color.from_c_color(result)

# Module-level convenience functions
_graphics = None

def init():
    """Initialize graphics library"""
    global _graphics
    if _graphics is None:
        _graphics = Graphics()
    return _graphics

def get_version():
    """Get library version"""
    return ffi.string(lib.ug_get_version()).decode('utf-8')

def get_platform_caps():
    """Get platform capabilities"""
    caps = lib.ug_get_platform_caps()
    return {
        'has_avx2': caps.has_avx2,
        'has_neon': caps.has_neon,
        'has_drm': caps.has_drm,
        'has_wayland': caps.has_wayland,
        'gpu_vendor': ffi.string(caps.gpu_vendor).decode('utf-8'),
        'platform_name': ffi.string(caps.platform_name).decode('utf-8')
    }

# Export main classes and functions
__all__ = ['Graphics', 'Surface', 'Color', 'GraphicsError', 'init', 'get_version', 'get_platform_caps']
'''

    return wrapper_code


def main():
    """Main build function"""
    print("Building CFFI bindings for Unhinged Graphics Library...")

    # Build CFFI bindings
    ffibuilder = build_cffi_bindings()

    # Generate output directory
    output_dir = Path("/home/e-bliss-station-1/Projects/Unhinged/libs/graphics/build") / "python_bindings"
    output_dir.mkdir(exist_ok=True)

    # Compile the extension
    ffibuilder.compile(tmpdir=str(output_dir))

    # Create Python wrapper
    wrapper_code = create_python_wrapper()
    wrapper_file = output_dir / "unhinged_graphics.py"
    with open(wrapper_file, "w") as f:
        f.write(wrapper_code)

    # Create __init__.py
    init_file = output_dir / "__init__.py"
    with open(init_file, "w") as f:
        f.write("from .unhinged_graphics import *\\n")

    print(f"CFFI bindings generated in: {output_dir}")
    print("Python bindings are ready!")


if __name__ == "__main__":
    main()
