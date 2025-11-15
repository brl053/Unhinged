# GTK4 Integration Guide: Using Headless Generate Commands

## Overview

The new headless `./unhinged generate` commands are designed to be called from the GTK4 UI. This guide shows how to integrate them into the OS Chatroom view.

## Current Implementation (Before)

```python
# In control/gtk4_gui/views/chatroom_view.py
from libs.services import ImageGenerationService

def _handle_slash_image_command(self, prompt: str):
    """Handle /image command"""
    service = ImageGenerationService()
    result = service.generate_image(
        prompt=prompt,
        num_inference_steps=20,
        guidance_scale=7.5,
        height=512,
        width=512
    )
    self._display_generated_image(result)
```

**Problems**:
- Direct library dependency
- UI and generation logic mixed
- Hard to test independently
- Hard to add new models

## New Implementation (After)

```python
# In control/gtk4_gui/views/chatroom_view.py
import subprocess
import json
from pathlib import Path

def _handle_slash_image_command(self, prompt: str):
    """Handle /image command using headless CLI"""
    try:
        # Call headless command
        result = subprocess.run([
            str(Path(__file__).parent.parent.parent / "unhinged"),
            "generate", "image", "stable-diffusion",
            prompt,
            "--format", "json"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode != 0:
            self._add_error_message(f"Generation failed: {result.stderr}")
            return
        
        # Parse JSON output
        data = json.loads(result.stdout)
        self._display_generated_image(data)
        
    except subprocess.TimeoutExpired:
        self._add_error_message("Generation timeout (>2 minutes)")
    except json.JSONDecodeError:
        self._add_error_message("Invalid response from generation service")
    except Exception as e:
        self._add_error_message(f"Generation error: {e}")
```

**Benefits**:
- No direct library dependency
- Generation logic is separate
- Easy to test independently
- Easy to add new models
- Can be called from anywhere

## Step-by-Step Integration

### Step 1: Update Imports
```python
import subprocess
import json
from pathlib import Path
```

### Step 2: Create Helper Method
```python
def _run_generate_command(self, command_args: list, timeout: int = 120) -> dict:
    """Run headless generate command and return result"""
    try:
        project_root = Path(__file__).parent.parent.parent
        cmd = [str(project_root / "unhinged")] + command_args
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")
        
        return json.loads(result.stdout)
        
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"Command timeout after {timeout}s")
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON response from command")
```

### Step 3: Update Image Command Handler
```python
def _handle_slash_image_command(self, prompt: str):
    """Handle /image command using headless CLI"""
    self._add_chat_message("You", f"/image {prompt}", "user")
    thinking_box = self._add_thinking_indicator()
    
    def generate_thread():
        try:
            # Call headless command
            result = self._run_generate_command([
                "generate", "image", "stable-diffusion",
                prompt,
                "--format", "json"
            ])
            
            # Display result on main thread
            GLib.idle_add(self._display_generated_image, thinking_box, result, prompt)
            
        except Exception as e:
            GLib.idle_add(self._add_error_message, f"Generation failed: {e}")
    
    # Run in background thread
    import threading
    thread = threading.Thread(target=generate_thread, daemon=True)
    thread.start()
```

### Step 4: Add Video Command Handler
```python
def _handle_slash_video_command(self, prompt: str):
    """Handle /video command using headless CLI"""
    self._add_chat_message("You", f"/video {prompt}", "user")
    thinking_box = self._add_thinking_indicator()
    
    def generate_thread():
        try:
            result = self._run_generate_command([
                "generate", "video", "stable-diffusion",
                prompt,
                "--duration", "30",
                "--format", "json"
            ])
            
            GLib.idle_add(self._display_generated_video, thinking_box, result, prompt)
            
        except Exception as e:
            GLib.idle_add(self._add_error_message, f"Video generation failed: {e}")
    
    import threading
    thread = threading.Thread(target=generate_thread, daemon=True)
    thread.start()
```

### Step 5: Add Model Selection
```python
def _handle_slash_image_command(self, prompt: str, model: str = "stable-diffusion"):
    """Handle /image command with model selection"""
    # Parse: /image model:sdxl steps:40 a beautiful landscape
    parts = prompt.split()
    model = "stable-diffusion"
    steps = 20
    
    for part in parts:
        if part.startswith("model:"):
            model = part.split(":")[1]
        elif part.startswith("steps:"):
            steps = int(part.split(":")[1])
    
    # Remove model/steps from prompt
    prompt_text = " ".join([
        p for p in parts 
        if not p.startswith("model:") and not p.startswith("steps:")
    ])
    
    # Call with selected model
    result = self._run_generate_command([
        "generate", "image", model,
        prompt_text,
        "--steps", str(steps),
        "--format", "json"
    ])
```

## Usage Examples

### Basic Image Generation
```
/image a beautiful landscape
```

### With Model Selection
```
/image model:sdxl a professional portrait
```

### With Custom Steps
```
/image model:sdxl steps:40 a detailed landscape
```

### Video Generation
```
/video a sunset over the ocean
```

### With Duration
```
/video duration:60 a dancing figure
```

## Error Handling

```python
def _handle_generation_error(self, error: Exception):
    """Handle generation errors gracefully"""
    if isinstance(error, TimeoutError):
        self._add_error_message("⏱️ Generation timeout - try simpler prompt")
    elif isinstance(error, RuntimeError):
        self._add_error_message(f"❌ Generation failed: {error}")
    elif isinstance(error, ValueError):
        self._add_error_message("❌ Invalid response from generation service")
    else:
        self._add_error_message(f"❌ Unexpected error: {error}")
```

## Testing

### Test the Integration
```python
# In test_chatroom_integration.py
def test_image_generation_command():
    """Test /image command calls headless CLI"""
    view = ChatroomView()
    
    # Mock subprocess
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = json.dumps({
            "image_path": "/tmp/test.png",
            "generation_time": 12.5
        })
        
        view._handle_slash_image_command("a landscape")
        
        # Verify command was called
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "generate" in args
        assert "image" in args
```

## Migration Path

### Phase 1: Add Headless Commands (Done)
- ✅ Create `control/generate_cli.py`
- ✅ Create `./unhinged generate` command
- ✅ Create man page and documentation

### Phase 2: Update GTK4 UI (Next)
- [ ] Update `chatroom_view.py` to use subprocess
- [ ] Add model selection to UI
- [ ] Add video generation support
- [ ] Remove direct library imports

### Phase 3: Extend Functionality
- [ ] Add YOLO analysis command
- [ ] Add model management commands
- [ ] Add generation history
- [ ] Add batch generation

## Benefits

1. **Separation of Concerns**
   - UI doesn't know about generation details
   - Generation logic is independent
   - Easy to test each part

2. **Flexibility**
   - Can call from any UI (GTK4, web, CLI)
   - Can add new models without UI changes
   - Can run on different machines

3. **Maintainability**
   - Simpler code in UI
   - Easier to debug
   - Easier to add features

4. **Scalability**
   - Can run generation on separate machine
   - Can queue multiple requests
   - Can add load balancing

## Troubleshooting

### Command Not Found
```python
# Make sure unhinged script is executable
import os
os.chmod(str(project_root / "unhinged"), 0o755)
```

### JSON Parse Error
```python
# Print raw output for debugging
print(f"stdout: {result.stdout}")
print(f"stderr: {result.stderr}")
```

### Timeout Issues
```python
# Increase timeout for slower systems
result = self._run_generate_command(args, timeout=300)  # 5 minutes
```

