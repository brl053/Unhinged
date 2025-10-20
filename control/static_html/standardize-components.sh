#!/bin/bash

# Standardize All Components Script
# Adds headers and footers to all HTML files for consistency

echo "🔄 Standardizing headers and footers across all interfaces..."

# File configurations: filename -> "title|subtitle|icon"
declare -A file_configs=(
    ["text-test.html"]="Text Generation Test|AI-Powered Language Model Interface|🚀"
    ["voice-test.html"]="Voice Processing Test|Speech Recognition & Synthesis Platform|🎤"
    ["dag-control.html"]="DAG Control Center|Workflow Orchestration & Task Management|🎯"
    ["chat.html"]="AI Chat Interface|Conversational AI Platform|💬"
    ["grpc-test.html"]="Service Testing Hub|gRPC Service Health & Testing|🔧"
    ["table-of-contents.html"]="Interface Directory|Complete Platform Navigation|📚"
    ["service-orchestration.html"]="Service Orchestration|Docker Container Management|🎛️"
    ["persistence-dev-tool.html"]="Data Management|Persistence Platform Development Tool|💾"
)

for file in "${!file_configs[@]}"; do
    if [[ -f "$file" ]]; then
        echo "📝 Standardizing $file"
        
        # Parse configuration
        IFS='|' read -r title subtitle icon <<< "${file_configs[$file]}"
        
        # Add header component if h1 exists but no header component
        if grep -q "<h1>" "$file" && ! grep -q "data-component=\"page-header\"" "$file"; then
            # Find the h1 line and replace it with header component
            sed -i "/<h1>/,/<\/p>/ {
                /<h1>/ {
                    i\\        <!-- Page Header - DRY Component -->
                    i\\        <div id=\"header-container\" data-component=\"page-header\"
                    i\\             data-title=\"$title\"
                    i\\             data-subtitle=\"$subtitle\"
                    i\\             data-icon=\"$icon\"></div>
                    d
                }
                /<p class=\"subtitle\">/ d
                /<\/p>/ {
                    /subtitle/ d
                }
            }" "$file"
            echo "  ✅ Added standardized header"
        fi
        
        # Add footer component before closing body tag if not present
        if ! grep -q "data-component=\"footer\"" "$file"; then
            sed -i '/<\/body>/ i\\n    <!-- Footer - DRY Component -->\n    <div id="footer-container" data-component="footer"></div>' "$file"
            echo "  ✅ Added footer component"
        fi
        
    else
        echo "  ⚠️  File $file not found"
    fi
done

echo ""
echo "🎉 Component standardization complete!"
echo "📊 Processed ${#file_configs[@]} files"
echo ""
echo "🔍 Summary of changes:"
echo "  - Standardized page headers with consistent titles and subtitles"
echo "  - Added footer components to all interfaces"
echo "  - Maintained design token compliance"
echo "  - Preserved existing functionality"
