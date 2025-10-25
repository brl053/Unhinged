#!/bin/bash

# Comprehensive logging analysis script for the entire Unhinged codebase
# This script finds all existing logging patterns and generates migration statistics

set -e

PROJECT_ROOT="${1:-$(pwd)}"
OUTPUT_FILE="${2:-logging_analysis_$(date +%Y%m%d_%H%M%S).txt}"

echo "🔍 Analyzing logging patterns across Unhinged codebase..."
echo "📁 Project root: $PROJECT_ROOT"
echo "📄 Output file: $OUTPUT_FILE"
echo ""

# Create output file
cat > "$OUTPUT_FILE" << EOF
# Unhinged Codebase Logging Analysis
Generated on: $(date)
Project root: $PROJECT_ROOT

EOF

echo "## Summary Statistics" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Function to count patterns in files
count_pattern() {
    local pattern="$1"
    local path="$2"
    local description="$3"
    
    if [ -d "$PROJECT_ROOT/$path" ]; then
        local count=$(find "$PROJECT_ROOT/$path" -name "*.py" -o -name "*.kt" -o -name "*.js" -o -name "*.ts" | \
                     xargs grep -c "$pattern" 2>/dev/null | \
                     awk -F: '{sum += $2} END {print sum+0}')
        echo "- **$description**: $count instances in $path"
        echo "- **$description**: $count instances in $path" >> "$OUTPUT_FILE"
    fi
}

# Count different logging patterns
echo "### Logging Pattern Counts"
echo "### Logging Pattern Counts" >> "$OUTPUT_FILE"
echo ""
echo "" >> "$OUTPUT_FILE"

count_pattern "print(" "control/native_gui" "Native GUI print statements"
count_pattern "logger\." "services" "Python service logging calls"
count_pattern "logging\." "services" "Python service direct logging calls"
count_pattern "println\|Logger" "platforms" "Kotlin logging statements"
count_pattern "console\." "." "JavaScript/TypeScript console calls"

echo ""
echo "" >> "$OUTPUT_FILE"

# Detailed analysis by component
echo "## Detailed Analysis by Component" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Native GUI Analysis
echo "### 🖥️ Native GUI (control/native_gui/)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [ -d "$PROJECT_ROOT/control/native_gui" ]; then
    echo "#### Print Statement Distribution" >> "$OUTPUT_FILE"
    find "$PROJECT_ROOT/control/native_gui" -name "*.py" -exec basename {} \; | \
    while read file; do
        full_path=$(find "$PROJECT_ROOT/control/native_gui" -name "$file" | head -1)
        if [ -f "$full_path" ]; then
            count=$(grep -c "print(" "$full_path" 2>/dev/null || echo "0")
            if [ "$count" -gt 0 ] 2>/dev/null; then
                echo "- $file: $count print statements" >> "$OUTPUT_FILE"
            fi
        fi
    done
    
    echo "" >> "$OUTPUT_FILE"
    echo "#### Emoji Pattern Analysis" >> "$OUTPUT_FILE"
    echo "- ✅ Success messages: $(find "$PROJECT_ROOT/control/native_gui" -name "*.py" | xargs grep -c "print.*✅" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')" >> "$OUTPUT_FILE"
    echo "- ❌ Error messages: $(find "$PROJECT_ROOT/control/native_gui" -name "*.py" | xargs grep -c "print.*❌" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')" >> "$OUTPUT_FILE"
    echo "- 🚀 Startup messages: $(find "$PROJECT_ROOT/control/native_gui" -name "*.py" | xargs grep -c "print.*🚀" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')" >> "$OUTPUT_FILE"
    echo "- 🎯 Activity messages: $(find "$PROJECT_ROOT/control/native_gui" -name "*.py" | xargs grep -c "print.*🎯" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')" >> "$OUTPUT_FILE"
    echo "- ⚠️ Warning messages: $(find "$PROJECT_ROOT/control/native_gui" -name "*.py" | xargs grep -c "print.*⚠️" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')" >> "$OUTPUT_FILE"
fi

echo "" >> "$OUTPUT_FILE"

# Python Services Analysis
echo "### 🐍 Python Services (services/)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [ -d "$PROJECT_ROOT/services" ]; then
    echo "#### Service-by-Service Breakdown" >> "$OUTPUT_FILE"
    for service_dir in "$PROJECT_ROOT/services"/*; do
        if [ -d "$service_dir" ]; then
            service_name=$(basename "$service_dir")
            logging_count=$(find "$service_dir" -name "*.py" | xargs grep -c "logger\.\|logging\." 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
            print_count=$(find "$service_dir" -name "*.py" | xargs grep -c "print(" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
            
            if [ "$logging_count" -gt 0 ] || [ "$print_count" -gt 0 ]; then
                echo "- **$service_name**: $logging_count logging calls, $print_count print statements" >> "$OUTPUT_FILE"
            fi
        fi
    done
fi

echo "" >> "$OUTPUT_FILE"

# Kotlin Platforms Analysis
echo "### ☕ Kotlin Platforms (platforms/)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [ -d "$PROJECT_ROOT/platforms" ]; then
    echo "#### Platform-by-Platform Breakdown" >> "$OUTPUT_FILE"
    for platform_dir in "$PROJECT_ROOT/platforms"/*; do
        if [ -d "$platform_dir" ]; then
            platform_name=$(basename "$platform_dir")
            kotlin_logging=$(find "$platform_dir" -name "*.kt" | xargs grep -c "logger\.\|Logger\.\|println" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
            
            if [ "$kotlin_logging" -gt 0 ]; then
                echo "- **$platform_name**: $kotlin_logging logging statements" >> "$OUTPUT_FILE"
            fi
        fi
    done
fi

echo "" >> "$OUTPUT_FILE"

# Control Systems Analysis
echo "### 🎛️ Control Systems (control/)" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

if [ -d "$PROJECT_ROOT/control" ]; then
    echo "#### Control Component Breakdown" >> "$OUTPUT_FILE"
    for control_dir in "$PROJECT_ROOT/control"/*; do
        if [ -d "$control_dir" ] && [ "$(basename "$control_dir")" != "native_gui" ]; then
            component_name=$(basename "$control_dir")
            logging_count=$(find "$control_dir" -name "*.py" | xargs grep -c "logger\.\|logging\." 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
            print_count=$(find "$control_dir" -name "*.py" | xargs grep -c "print(" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
            
            if [ "$logging_count" -gt 0 ] || [ "$print_count" -gt 0 ]; then
                echo "- **$component_name**: $logging_count logging calls, $print_count print statements" >> "$OUTPUT_FILE"
            fi
        fi
    done
fi

echo "" >> "$OUTPUT_FILE"

# Migration Priority Recommendations
echo "## Migration Priority Recommendations" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Calculate totals for priority ranking
gui_prints=$(find "$PROJECT_ROOT/control/native_gui" -name "*.py" | xargs grep -c "print(" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
service_logging=$(find "$PROJECT_ROOT/services" -name "*.py" | xargs grep -c "logger\.\|logging\." 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')
kotlin_logging=$(find "$PROJECT_ROOT/platforms" -name "*.kt" | xargs grep -c "logger\.\|Logger\.\|println" 2>/dev/null | awk -F: '{sum += $2} END {print sum+0}')

echo "### 🔴 HIGH PRIORITY" >> "$OUTPUT_FILE"
echo "1. **Native GUI Migration** - $gui_prints print statements" >> "$OUTPUT_FILE"
echo "   - High user visibility impact" >> "$OUTPUT_FILE"
echo "   - Easy to migrate with provided scripts" >> "$OUTPUT_FILE"
echo "   - Immediate improvement in debugging capabilities" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🟡 MEDIUM PRIORITY" >> "$OUTPUT_FILE"
echo "2. **Python Services Migration** - $service_logging logging calls" >> "$OUTPUT_FILE"
echo "   - Core AI service observability" >> "$OUTPUT_FILE"
echo "   - Structured event logging for better monitoring" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### 🟢 LOW PRIORITY" >> "$OUTPUT_FILE"
echo "3. **Kotlin Platforms Migration** - $kotlin_logging logging statements" >> "$OUTPUT_FILE"
echo "   - Already well-structured" >> "$OUTPUT_FILE"
echo "   - Mainly configuration changes needed" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# Migration Commands
echo "## Migration Commands" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### Native GUI Migration" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
echo "# Analyze native GUI logging patterns" >> "$OUTPUT_FILE"
echo "python libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "# Apply native GUI migration" >> "$OUTPUT_FILE"
echo "python libs/event-framework/migration_scripts/migrate_native_gui.py control/native_gui --apply" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### Python Services Migration" >> "$OUTPUT_FILE"
echo '```bash' >> "$OUTPUT_FILE"
echo "# Analyze all Python services" >> "$OUTPUT_FILE"
echo "python libs/event-framework/migration_scripts/migrate_python_services.py services" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"
echo "# Migrate specific service" >> "$OUTPUT_FILE"
echo "python libs/event-framework/migration_scripts/migrate_python_services.py services speech-to-text --apply" >> "$OUTPUT_FILE"
echo '```' >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

# File-specific recommendations
echo "## High-Impact Files for Immediate Migration" >> "$OUTPUT_FILE"
echo "" >> "$OUTPUT_FILE"

echo "### Native GUI Files (Top 10 by print count)" >> "$OUTPUT_FILE"
if [ -d "$PROJECT_ROOT/control/native_gui" ]; then
    find "$PROJECT_ROOT/control/native_gui" -name "*.py" -exec sh -c 'echo "$(grep -c "print(" "$1" 2>/dev/null || echo 0):$1"' _ {} \; | \
    sort -nr | head -10 | while IFS=: read count file; do
        if [ "$count" -gt 0 ]; then
            echo "- $(basename "$file"): $count print statements" >> "$OUTPUT_FILE"
        fi
    done
fi

echo "" >> "$OUTPUT_FILE"
echo "---" >> "$OUTPUT_FILE"
echo "Generated by: libs/event-framework/migration_scripts/analyze_all_logging.sh" >> "$OUTPUT_FILE"

# Display summary to console
echo "📊 Analysis complete!"
echo ""
echo "📈 Key Statistics:"
echo "  - Native GUI print statements: $gui_prints"
echo "  - Python service logging calls: $service_logging"
echo "  - Kotlin logging statements: $kotlin_logging"
echo ""
echo "📄 Detailed analysis saved to: $OUTPUT_FILE"
echo ""
echo "🚀 Next steps:"
echo "  1. Review the analysis file: cat $OUTPUT_FILE"
echo "  2. Start with Native GUI migration (highest impact)"
echo "  3. Use the provided migration scripts in libs/event-framework/migration_scripts/"
echo ""
echo "💡 Migration scripts available:"
echo "  - migrate_native_gui.py (for GUI components)"
echo "  - migrate_python_services.py (for Python services)"
