#!/bin/bash

# ============================================================================
# HTML Interface Testing Workflow Validation
# Tests the complete Make-based HTML testing system
# ============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

print_header() {
    echo -e "${PURPLE}🧪 HTML Interface Testing Workflow Validation${NC}"
    echo "=================================================="
}

test_make_targets() {
    print_info "Testing Make targets..."
    
    # Test sanity check
    print_info "Running sanity check..."
    if make html-sanity > /dev/null 2>&1; then
        print_success "html-sanity target works"
    else
        print_error "html-sanity target failed"
        return 1
    fi
    
    # Test setup
    print_info "Testing setup..."
    if make html-setup > /dev/null 2>&1; then
        print_success "html-setup target works"
    else
        print_error "html-setup target failed"
        return 1
    fi
    
    # Test list
    print_info "Testing list..."
    if make html-list > /dev/null 2>&1; then
        print_success "html-list target works"
    else
        print_error "html-list target failed"
        return 1
    fi
    
    print_success "All Make targets working"
}

test_file_structure() {
    print_info "Testing file structure..."
    
    # Check static_html files
    local files=("index.html" "image-test.html" "voice-test.html" "text-test.html")
    for file in "${files[@]}"; do
        if [ -f "static_html/$file" ]; then
            print_success "static_html/$file exists"
        else
            print_error "static_html/$file missing"
            return 1
        fi
    done
    
    # Check main dashboard
    if [ -f "unhinged-health-dashboard.html" ]; then
        print_success "unhinged-health-dashboard.html exists"
    else
        print_error "unhinged-health-dashboard.html missing"
        return 1
    fi
    
    # Check symlinks
    if [ -d "static_html/html-links" ]; then
        print_success "static_html/html-links directory exists"

        local symlinks=("dashboard.html" "vision.html" "audio.html" "context.html")
        for link in "${symlinks[@]}"; do
            if [ -L "static_html/html-links/$link" ]; then
                print_success "static_html/html-links/$link symlink exists"
            else
                print_error "static_html/html-links/$link symlink missing"
                return 1
            fi
        done
    else
        print_error "static_html/html-links directory missing"
        return 1
    fi
    
    print_success "File structure validation complete"
}

test_launcher_script() {
    print_info "Testing launcher script..."

    if [ -x "static_html/html-links/open.sh" ]; then
        print_success "Launcher script is executable"

        # Test menu display
        if ./static_html/html-links/open.sh > /dev/null 2>&1; then
            print_success "Launcher script menu works"
        else
            print_error "Launcher script menu failed"
            return 1
        fi
    else
        print_error "Launcher script not executable"
        return 1
    fi

    print_success "Launcher script validation complete"
}

test_makefile_integration() {
    print_info "Testing Makefile integration..."
    
    # Check if HTML targets are in help
    if make help | grep -q "HTML Testing"; then
        print_success "HTML Testing section in help"
    else
        print_error "HTML Testing section missing from help"
        return 1
    fi
    
    # Check aliases
    local aliases=("test-ui" "ui-setup" "ui-sanity")
    for alias in "${aliases[@]}"; do
        if make -n "$alias" > /dev/null 2>&1; then
            print_success "Alias '$alias' works"
        else
            print_error "Alias '$alias' failed"
            return 1
        fi
    done
    
    print_success "Makefile integration validation complete"
}

test_walking_skeleton_workflow() {
    print_info "Testing walking skeleton workflow..."
    
    # Test quick workflow
    if make test-ui-quick > /dev/null 2>&1; then
        print_success "test-ui-quick workflow works"
    else
        print_error "test-ui-quick workflow failed"
        return 1
    fi
    
    # Test validation workflow (without services)
    if make html-sanity > /dev/null 2>&1; then
        print_success "Validation workflow works"
    else
        print_error "Validation workflow failed"
        return 1
    fi
    
    print_success "Walking skeleton workflow validation complete"
}

run_comprehensive_test() {
    print_header
    
    local tests=(
        "test_file_structure"
        "test_make_targets"
        "test_launcher_script"
        "test_makefile_integration"
        "test_walking_skeleton_workflow"
    )
    
    local passed=0
    local total=${#tests[@]}
    
    for test in "${tests[@]}"; do
        echo ""
        if $test; then
            ((passed++))
        else
            print_error "Test $test failed"
        fi
    done
    
    echo ""
    echo "=================================================="
    if [ $passed -eq $total ]; then
        print_success "All tests passed! ($passed/$total)"
        print_info "HTML interface testing system is fully functional"
        echo ""
        print_info "Quick start commands:"
        echo "  make test-ui           # Launch testing hub"
        echo "  make html-dashboard    # Open health dashboard"
        echo "  make validate-system   # Complete validation"
        return 0
    else
        print_error "Some tests failed ($passed/$total)"
        return 1
    fi
}

# Run the comprehensive test
run_comprehensive_test
