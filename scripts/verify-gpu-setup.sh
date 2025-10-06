#!/bin/bash

echo "🚀 GPU Configuration Verification Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

echo -e "${BLUE}Step 1: Checking NVIDIA Driver${NC}"
nvidia-smi > /dev/null 2>&1
print_status $? "NVIDIA Driver installed and working"

echo -e "\n${BLUE}Step 2: Checking Docker GPU Runtime${NC}"
docker info 2>/dev/null | grep -i nvidia > /dev/null
print_status $? "Docker NVIDIA runtime configured"

echo -e "\n${BLUE}Step 3: Testing Docker GPU Access${NC}"
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi > /dev/null 2>&1
print_status $? "Docker can access GPU"

echo -e "\n${BLUE}Step 4: Checking Ollama Container Status${NC}"
docker ps | grep ollama-service > /dev/null
print_status $? "Ollama container is running"

echo -e "\n${BLUE}Step 5: Testing Ollama GPU Access${NC}"
if docker ps | grep ollama-service > /dev/null; then
    docker exec ollama-service nvidia-smi > /dev/null 2>&1
    print_status $? "Ollama container can access GPU"
else
    echo -e "${YELLOW}⚠️  Ollama container not running - skipping GPU test${NC}"
fi

echo -e "\n${BLUE}Step 6: Current VRAM Usage${NC}"
echo "Host VRAM usage:"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits | while read used total; do
    percentage=$((used * 100 / total))
    echo "  Used: ${used}MB / ${total}MB (${percentage}%)"
done

echo -e "\n${BLUE}Step 7: Performance Test${NC}"
if docker ps | grep ollama-service > /dev/null; then
    echo "Testing inference speed with DeepSeek-Coder..."
    start_time=$(date +%s)
    
    curl -s -X POST http://localhost:11434/api/generate \
        -H "Content-Type: application/json" \
        -d '{"model": "deepseek-coder:6.7b", "prompt": "Write a simple hello world function in Python", "stream": false}' \
        > /tmp/gpu_test_result.json 2>/dev/null
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if [ -f /tmp/gpu_test_result.json ] && [ -s /tmp/gpu_test_result.json ]; then
        echo "  Inference completed in ${duration} seconds"
        
        # Check if response contains actual content
        response_length=$(jq -r '.response | length' /tmp/gpu_test_result.json 2>/dev/null || echo "0")
        if [ "$response_length" -gt 10 ]; then
            echo -e "${GREEN}✅ GPU inference test successful${NC}"
            
            # Performance assessment
            if [ $duration -lt 15 ]; then
                echo -e "${GREEN}🚀 Excellent performance (GPU acceleration likely working)${NC}"
            elif [ $duration -lt 30 ]; then
                echo -e "${YELLOW}⚠️  Moderate performance (check GPU utilization)${NC}"
            else
                echo -e "${RED}🐌 Slow performance (likely CPU inference)${NC}"
            fi
        else
            echo -e "${RED}❌ GPU inference test failed - no valid response${NC}"
        fi
    else
        echo -e "${RED}❌ GPU inference test failed - no response${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Ollama container not running - skipping performance test${NC}"
fi

echo -e "\n${BLUE}Step 8: VRAM Usage After Test${NC}"
echo "VRAM usage after inference:"
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader,nounits | while read used total util; do
    percentage=$((used * 100 / total))
    echo "  Memory: ${used}MB / ${total}MB (${percentage}%)"
    echo "  GPU Utilization: ${util}%"
done

echo -e "\n${BLUE}Summary${NC}"
echo "======="
echo "If you see:"
echo "• ✅ All checks passing + inference < 15 seconds = GPU acceleration working"
echo "• ❌ Docker GPU runtime issues = Run nvidia-container-toolkit installation"
echo "• 🐌 Slow inference (>30s) = Still using CPU, check container GPU access"
echo ""
echo "Expected performance with GPU:"
echo "• DeepSeek-Coder: ~5-10 seconds (vs ~47s on CPU)"
echo "• Dolphin-Mixtral: ~15-25 seconds (vs ~100s on CPU)"
echo ""
echo "For detailed logs, check: docker logs ollama-service"
