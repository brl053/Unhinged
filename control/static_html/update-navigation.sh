#!/bin/bash

# Update Navigation to DRY Components Script
# Replaces hardcoded navigation with component injection

echo "🔄 Updating navigation to DRY components..."

# Files to update with their active page IDs
declare -A files=(
    ["text-test.html"]="text"
    ["grpc-test.html"]="grpc"
    ["table-of-contents.html"]="toc"
    ["chat.html"]="chat"
    ["service-orchestration.html"]="orchestration"
    ["dag-control.html"]="dag"
    ["voice-test.html"]="voice"
    ["persistence-dev-tool.html"]="persistence"
)

for file in "${!files[@]}"; do
    active_page="${files[$file]}"
    echo "📝 Updating $file (active: $active_page)"
    
    # Add components.js script if not present
    if ! grep -q "shared/components.js" "$file"; then
        # Find the line with theme.css and add components.js after it
        sed -i '/shared\/theme\.css/a\    <script src="shared/components.js"></script>' "$file"
        echo "  ✅ Added components.js script"
    fi
    
    # Replace navigation HTML with component container
    # This is a complex sed operation to replace multi-line navigation blocks
    if grep -q '<div class="navigation">' "$file"; then
        # Create temporary file with replacement
        awk '
        /<div class="navigation">/ {
            print "        <!-- Navigation - DRY Component -->"
            print "        <div id=\"nav-container\" data-component=\"navigation\" data-active=\"'$active_page'\"></div>"
            # Skip lines until we find the closing </div>
            while (getline > 0) {
                if ($0 ~ /<\/div>/) break
            }
            next
        }
        { print }
        ' "$file" > "${file}.tmp" && mv "${file}.tmp" "$file"
        echo "  ✅ Replaced navigation HTML with component"
    else
        echo "  ⚠️  No navigation block found"
    fi
done

echo "🎉 Navigation update complete!"
echo "📊 Updated ${#files[@]} files with DRY navigation components"
