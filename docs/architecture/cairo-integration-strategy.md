# 🎨 Cairo Integration Strategy for Wayland Rendering

> **Purpose**: Maintain existing Cairo graphics capabilities within the new Wayland rendering architecture
> **Target**: Seamless integration of 2D graphics with OpenGL ES acceleration
> **Status**: Integration Design Complete

## 🎯 Executive Summary

This strategy preserves all existing Cairo-based custom drawing capabilities while integrating them into the new OpenGL ES + Wayland rendering pipeline. The hybrid approach leverages Cairo's mature 2D graphics for UI elements and text rendering while using OpenGL ES for performance-critical operations.

## 🏗️ Current Cairo Usage Analysis

### Existing Cairo Implementation

Based on the codebase analysis, Cairo is currently used for:

**Custom Drawing Operations:**
- Status indicator graphics with smooth curves and gradients
- Vision overlay bounding boxes and detection markers
- Custom widget backgrounds with rounded corners
- Real-time audio visualization waveforms
- Mobile-responsive layout rendering

**Text and Typography:**
- Pango integration for complex text layout
- Multi-language text rendering
- Font scaling for responsive design
- Text measurement and positioning

**2D Graphics Primitives:**
- Vector graphics for icons and symbols
- Gradient fills and pattern rendering
- Path-based drawing operations
- Image compositing and blending

## 🔄 Hybrid Rendering Architecture

### Cairo + OpenGL ES Integration

**Rendering Pipeline Flow:**
```
Cairo 2D Graphics → Image Surface → OpenGL Texture → GPU Composition → Wayland Surface
```

**Component Classification:**
```python
class RenderingStrategy:
    """Determine optimal rendering approach per component"""
    
    @staticmethod
    def should_use_cairo(widget):
        """Components best suited for Cairo rendering"""
        return isinstance(widget, (
            TextWidget,           # Complex text layout
            IconWidget,           # Vector graphics
            StaticBackground,     # Simple shapes
            CustomPath,           # Vector paths
        ))
    
    @staticmethod
    def should_use_opengl(widget):
        """Components requiring GPU acceleration"""
        return isinstance(widget, (
            AnimatedWidget,       # Smooth animations
            VisionOverlay,        # Real-time graphics
            ParticleEffect,       # Complex effects
            VideoWidget,          # Hardware decode
        ))
```

### Texture Upload Strategy

**Cairo Surface to OpenGL Texture:**
```python
import cairo
import OpenGL.GLES2 as gl
import numpy as np

class CairoTextureManager:
    """Efficient Cairo surface to OpenGL texture conversion"""
    
    def __init__(self):
        self.texture_cache = {}
        self.surface_pool = []
        
    def create_texture_from_cairo(self, cairo_surface):
        """Convert Cairo surface to OpenGL texture"""
        # Get raw ARGB data from Cairo
        width = cairo_surface.get_width()
        height = cairo_surface.get_height()
        stride = cairo_surface.get_stride()
        
        # Cairo uses BGRA, OpenGL expects RGBA
        data = cairo_surface.get_data()
        rgba_data = self._convert_bgra_to_rgba(data, width, height)
        
        # Create OpenGL texture
        texture_id = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, texture_id)
        gl.glTexImage2D(
            gl.GL_TEXTURE_2D, 0, gl.GL_RGBA,
            width, height, 0,
            gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, rgba_data
        )
        
        # Set texture parameters for UI rendering
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
        
        return texture_id
    
    def _convert_bgra_to_rgba(self, bgra_data, width, height):
        """Convert Cairo's BGRA format to OpenGL's RGBA"""
        # Use numpy for efficient conversion
        bgra_array = np.frombuffer(bgra_data, dtype=np.uint8)
        bgra_array = bgra_array.reshape((height, width, 4))
        
        # Swap B and R channels
        rgba_array = bgra_array.copy()
        rgba_array[:, :, [0, 2]] = rgba_array[:, :, [2, 0]]
        
        return rgba_array.tobytes()
```

## 🎨 Component-Specific Integration

### Text Rendering with Pango

**Preserve Existing Text Pipeline:**
```python
class CairoTextRenderer:
    """Maintain existing Pango + Cairo text rendering"""
    
    def __init__(self, font_size=12, font_family="Ubuntu"):
        self.font_size = font_size
        self.font_family = font_family
        self.pango_layout = None
        
    def render_text_to_texture(self, text, max_width=None):
        """Render text using Cairo/Pango, return as OpenGL texture"""
        # Create Cairo surface for text
        temp_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
        temp_context = cairo.Context(temp_surface)
        
        # Set up Pango layout
        layout = PangoCairo.create_layout(temp_context)
        layout.set_text(text, -1)
        
        # Configure font
        font_desc = Pango.FontDescription(f"{self.font_family} {self.font_size}")
        layout.set_font_description(font_desc)
        
        if max_width:
            layout.set_width(max_width * Pango.SCALE)
            layout.set_wrap(Pango.WrapMode.WORD)
        
        # Get text dimensions
        text_width, text_height = layout.get_pixel_size()
        
        # Create properly sized surface
        text_surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, 
            text_width + 4,  # Small padding
            text_height + 4
        )
        text_context = cairo.Context(text_surface)
        
        # Render text
        text_context.set_source_rgba(1, 1, 1, 1)  # White text
        text_context.move_to(2, 2)  # Padding offset
        PangoCairo.show_layout(text_context, layout)
        
        # Convert to OpenGL texture
        return self.texture_manager.create_texture_from_cairo(text_surface)
```

### Custom Graphics Components

**Status Indicators with Cairo:**
```python
class StatusIndicatorRenderer:
    """Maintain existing Cairo-based status indicator graphics"""
    
    def render_status_indicator(self, status, size=32):
        """Render status indicator using Cairo, return as texture"""
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, size, size)
        ctx = cairo.Context(surface)
        
        # Clear background
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        
        # Draw status-specific graphics
        center_x, center_y = size // 2, size // 2
        radius = size // 3
        
        if status == "recording":
            # Red pulsing circle
            ctx.set_source_rgba(1.0, 0.2, 0.2, 0.8)
            ctx.arc(center_x, center_y, radius, 0, 2 * math.pi)
            ctx.fill()
            
        elif status == "processing":
            # Spinning gradient
            gradient = cairo.RadialGradient(center_x, center_y, 0, center_x, center_y, radius)
            gradient.add_color_stop_rgba(0, 0.2, 0.6, 1.0, 1.0)
            gradient.add_color_stop_rgba(1, 0.2, 0.6, 1.0, 0.3)
            ctx.set_source(gradient)
            ctx.arc(center_x, center_y, radius, 0, 2 * math.pi)
            ctx.fill()
            
        elif status == "ready":
            # Green checkmark
            ctx.set_source_rgba(0.2, 0.8, 0.2, 0.9)
            ctx.set_line_width(3)
            ctx.move_to(center_x - radius//2, center_y)
            ctx.line_to(center_x - radius//4, center_y + radius//3)
            ctx.line_to(center_x + radius//2, center_y - radius//3)
            ctx.stroke()
        
        return self.texture_manager.create_texture_from_cairo(surface)
```

### Vision Overlay Graphics

**Bounding Box Rendering:**
```python
class VisionOverlayRenderer:
    """Cairo-based vision detection overlay graphics"""
    
    def render_detection_overlay(self, detections, image_width, image_height):
        """Render detection bounding boxes using Cairo"""
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, image_width, image_height)
        ctx = cairo.Context(surface)
        
        # Transparent background
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_OVER)
        
        for detection in detections:
            x, y, w, h = detection['bbox']
            confidence = detection['confidence']
            label = detection['label']
            
            # Draw bounding box
            ctx.set_source_rgba(0.0, 1.0, 0.0, 0.8)  # Green
            ctx.set_line_width(2)
            ctx.rectangle(x, y, w, h)
            ctx.stroke()
            
            # Draw confidence background
            text_bg_height = 20
            ctx.set_source_rgba(0.0, 0.0, 0.0, 0.7)
            ctx.rectangle(x, y - text_bg_height, w, text_bg_height)
            ctx.fill()
            
            # Draw label text (would use Pango for complex text)
            ctx.set_source_rgba(1.0, 1.0, 1.0, 1.0)
            ctx.move_to(x + 4, y - 4)
            ctx.show_text(f"{label} {confidence:.2f}")
        
        return self.texture_manager.create_texture_from_cairo(surface)
```

## 🚀 Performance Optimizations

### Texture Caching Strategy

**Smart Cache Management:**
```python
class CairoTextureCache:
    """Intelligent caching for Cairo-rendered textures"""
    
    def __init__(self, max_cache_size=50):
        self.cache = {}
        self.usage_count = {}
        self.max_size = max_cache_size
        
    def get_or_create_texture(self, cache_key, render_func):
        """Get cached texture or create new one"""
        if cache_key in self.cache:
            self.usage_count[cache_key] += 1
            return self.cache[cache_key]
        
        # Create new texture
        texture_id = render_func()
        
        # Manage cache size
        if len(self.cache) >= self.max_size:
            self._evict_least_used()
        
        self.cache[cache_key] = texture_id
        self.usage_count[cache_key] = 1
        return texture_id
    
    def _evict_least_used(self):
        """Remove least frequently used texture"""
        least_used_key = min(self.usage_count, key=self.usage_count.get)
        texture_id = self.cache.pop(least_used_key)
        self.usage_count.pop(least_used_key)
        
        # Clean up OpenGL texture
        gl.glDeleteTextures(1, [texture_id])
```

### Surface Pooling

**Reuse Cairo Surfaces:**
```python
class CairoSurfacePool:
    """Pool Cairo surfaces to reduce allocation overhead"""
    
    def __init__(self):
        self.pools = {}  # size -> [surfaces]
        
    def get_surface(self, width, height, format=cairo.FORMAT_ARGB32):
        """Get pooled surface or create new one"""
        size_key = (width, height, format)
        
        if size_key in self.pools and self.pools[size_key]:
            surface = self.pools[size_key].pop()
            # Clear surface for reuse
            ctx = cairo.Context(surface)
            ctx.set_operator(cairo.OPERATOR_CLEAR)
            ctx.paint()
            return surface
        
        # Create new surface
        return cairo.ImageSurface(format, width, height)
    
    def return_surface(self, surface):
        """Return surface to pool for reuse"""
        width = surface.get_width()
        height = surface.get_height()
        format = surface.get_format()
        size_key = (width, height, format)
        
        if size_key not in self.pools:
            self.pools[size_key] = []
        
        # Limit pool size to prevent memory bloat
        if len(self.pools[size_key]) < 5:
            self.pools[size_key].append(surface)
```

## 🔧 Migration Implementation Plan

### Phase 1: Infrastructure Setup (Week 1)
1. Implement `CairoTextureManager` for surface-to-texture conversion
2. Create `CairoTextureCache` for performance optimization
3. Set up `CairoSurfacePool` for memory efficiency
4. Test basic Cairo → OpenGL texture pipeline

### Phase 2: Component Integration (Week 2)
1. Migrate text rendering to hybrid approach
2. Convert status indicators to texture-based rendering
3. Implement vision overlay texture generation
4. Test performance with existing UI components

### Phase 3: Optimization (Week 3)
1. Implement intelligent caching strategies
2. Optimize texture upload performance
3. Add memory usage monitoring
4. Fine-tune rendering pipeline

### Phase 4: Advanced Features (Week 4)
1. Add dynamic texture resizing
2. Implement texture atlas optimization
3. Add Cairo animation support
4. Performance profiling and tuning

## 📊 Performance Targets

### Rendering Performance
- Cairo surface creation: <5ms for typical UI elements
- Texture upload: <2ms for 512x512 surface
- Cache hit rate: >80% for repeated elements
- Memory usage: <50MB for Cairo textures

### Quality Preservation
- Pixel-perfect text rendering
- Smooth vector graphics
- Accurate color reproduction
- Proper alpha blending

## 🎯 Success Metrics

### Compatibility Validation
- All existing Cairo graphics render correctly
- Text layout matches current implementation
- Custom drawing operations preserved
- Performance meets or exceeds current GTK4 implementation

### Integration Verification
- Seamless Cairo + OpenGL ES composition
- No visual artifacts or rendering glitches
- Proper memory management and cleanup
- Stable performance under load

This Cairo integration strategy ensures that the transition to direct Wayland rendering preserves all existing graphics capabilities while providing a foundation for enhanced performance through selective GPU acceleration.
