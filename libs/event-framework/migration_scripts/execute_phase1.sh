#!/bin/bash

# Phase 1 Execution Script: Native GUI Migration
# Migrates 827 print statements to structured GUI events

set -e

PROJECT_ROOT="${1:-$(pwd)}"
DRY_RUN="${2:-true}"

echo "🚀 Starting Phase 1: Native GUI Migration"
echo "📁 Project root: $PROJECT_ROOT"
echo "🔍 Dry run mode: $DRY_RUN"
echo ""

# Validate prerequisites
if [ ! -f "$PROJECT_ROOT/libs/event-framework/python/src/unhinged_events/__init__.py" ]; then
    echo "❌ Event framework not found. Please ensure it's properly installed."
    exit 1
fi

if [ ! -d "$PROJECT_ROOT/control/native_gui" ]; then
    echo "❌ Native GUI directory not found: $PROJECT_ROOT/control/native_gui"
    exit 1
fi

# Function to migrate a file with validation
migrate_file() {
    local file_path="$1"
    local description="$2"
    
    echo "🔄 Migrating: $description"
    echo "   File: $file_path"
    
    if [ ! -f "$PROJECT_ROOT/$file_path" ]; then
        echo "   ⚠️ File not found, skipping: $file_path"
        return
    fi
    
    # Count print statements before migration
    local before_count=$(grep -c "print(" "$PROJECT_ROOT/$file_path" 2>/dev/null || echo "0")
    echo "   📊 Print statements before: $before_count"
    
    if [ "$before_count" -eq 0 ]; then
        echo "   ✅ No print statements to migrate"
        return
    fi
    
    # Run migration script
    if [ "$DRY_RUN" = "true" ]; then
        echo "   🔍 [DRY RUN] Would migrate $before_count print statements"
    else
        python3 "$PROJECT_ROOT/libs/event-framework/migration_scripts/migrate_native_gui.py" \
                "$PROJECT_ROOT/$file_path" --apply
        
        # Count print statements after migration
        local after_count=$(grep -c "print(" "$PROJECT_ROOT/$file_path" 2>/dev/null || echo "0")
        local migrated_count=$((before_count - after_count))
        
        echo "   📊 Print statements after: $after_count"
        echo "   ✅ Migrated: $migrated_count statements"
        
        if [ "$after_count" -gt 0 ]; then
            echo "   ⚠️ Warning: $after_count print statements remain (may need manual review)"
        fi
    fi
    
    echo ""
}

# Phase 1 Day 1-2: High-Impact Files (Top 10)
echo "📅 Day 1-2: High-Impact Files Migration"
echo "========================================="

migrate_file "control/native_gui/tools/vision/camera_capture.py" "Vision Tool - Camera Capture (74 statements)"
migrate_file "control/native_gui/tools/chat/bridge/audio_test.py" "Audio Tool - Audio Test (60 statements)"
migrate_file "control/native_gui/tools/audio/speech_client.py" "Audio Tool - Speech Client (39 statements)"
migrate_file "control/native_gui/tools/chat/mobile_chat_tool.py" "Chat Tool - Mobile Chat (38 statements)"
migrate_file "control/native_gui/tools/screen/screen_capture.py" "Screen Tool - Screen Capture (36 statements)"
migrate_file "control/native_gui/tools/input/keyboard_capture.py" "Input Tool - Keyboard Capture (34 statements)"
migrate_file "control/native_gui/core/application.py" "Core GUI - Application (33 statements)"
migrate_file "control/native_gui/tools/input/hotkey_manager.py" "Input Tool - Hotkey Manager (32 statements)"
migrate_file "control/native_gui/tools/input/mouse_capture.py" "Input Tool - Mouse Capture (27 statements)"
migrate_file "control/native_gui/tools/api_dev/proto_browser.py" "API Dev Tool - Proto Browser (24 statements)"

echo "📅 Day 3: Core GUI Components"
echo "=============================="

migrate_file "control/native_gui/main_window.py" "Core GUI - Main Window (15 statements)"
migrate_file "control/native_gui/core/tool_manager.py" "Core GUI - Tool Manager (22 statements)"
migrate_file "control/native_gui/core/theme_manager.py" "Core GUI - Theme Manager (14 statements)"
migrate_file "control/native_gui/launcher.py" "Core GUI - Launcher (11 statements)"

echo "📅 Day 4: Input Tools & Remaining Components"
echo "============================================="

# Migrate all remaining files in input tools
if [ -d "$PROJECT_ROOT/control/native_gui/tools/input" ]; then
    for input_file in "$PROJECT_ROOT/control/native_gui/tools/input"/*.py; do
        if [ -f "$input_file" ]; then
            relative_path=$(echo "$input_file" | sed "s|$PROJECT_ROOT/||")
            filename=$(basename "$input_file")
            
            # Skip already migrated files
            if [[ "$filename" != "keyboard_capture.py" && "$filename" != "hotkey_manager.py" && "$filename" != "mouse_capture.py" ]]; then
                migrate_file "$relative_path" "Input Tool - $filename"
            fi
        fi
    done
fi

# Migrate remaining tool directories
echo "🔄 Migrating remaining tool components..."

for tool_dir in "$PROJECT_ROOT/control/native_gui/tools"/*; do
    if [ -d "$tool_dir" ]; then
        tool_name=$(basename "$tool_dir")
        
        # Skip already processed directories
        if [[ "$tool_name" != "vision" && "$tool_name" != "audio" && "$tool_name" != "chat" && "$tool_name" != "screen" && "$tool_name" != "input" && "$tool_name" != "api_dev" ]]; then
            for py_file in "$tool_dir"/*.py; do
                if [ -f "$py_file" ]; then
                    relative_path=$(echo "$py_file" | sed "s|$PROJECT_ROOT/||")
                    filename=$(basename "$py_file")
                    migrate_file "$relative_path" "$tool_name Tool - $filename"
                fi
            done
        fi
    fi
done

echo "📅 Day 5: Final Cleanup & Validation"
echo "===================================="

# Run comprehensive migration on any remaining files
echo "🔄 Running comprehensive scan for remaining print statements..."

remaining_files=$(find "$PROJECT_ROOT/control/native_gui" -name "*.py" -exec grep -l "print(" {} \; 2>/dev/null || true)

if [ -n "$remaining_files" ]; then
    echo "📋 Files with remaining print statements:"
    echo "$remaining_files" | while read -r file; do
        if [ -f "$file" ]; then
            count=$(grep -c "print(" "$file" 2>/dev/null || echo "0")
            relative_path=$(echo "$file" | sed "s|$PROJECT_ROOT/||")
            echo "   - $relative_path: $count statements"
            
            if [ "$DRY_RUN" = "false" ]; then
                migrate_file "$relative_path" "Cleanup - $(basename "$file")"
            fi
        fi
    done
else
    echo "✅ No remaining print statements found!"
fi

# Final statistics
echo ""
echo "📊 Phase 1 Migration Summary"
echo "============================"

total_remaining=$(find "$PROJECT_ROOT/control/native_gui" -name "*.py" -exec grep -c "print(" {} \; 2>/dev/null | awk '{sum += $1} END {print sum+0}')
echo "📈 Total remaining print statements: $total_remaining"

if [ "$total_remaining" -eq 0 ]; then
    echo "🎉 Phase 1 Complete! All print statements successfully migrated."
else
    echo "⚠️ $total_remaining print statements still need manual review."
fi

echo ""
echo "🔍 Next Steps:"
echo "1. Test GUI functionality: python3 control/native_gui/launcher.py"
echo "2. Check GUI logs tab for structured events"
echo "3. Validate no functionality regressions"
echo "4. Proceed to Phase 2 if all tests pass"

if [ "$DRY_RUN" = "true" ]; then
    echo ""
    echo "🚀 To execute actual migration, run:"
    echo "   $0 $PROJECT_ROOT false"
fi
