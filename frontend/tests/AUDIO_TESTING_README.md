# 🎵 Audio Pipeline E2E Testing System

## Overview

This comprehensive testing system validates the complete audio pipeline:
**Text → TTS → Audio File → STT → Text Comparison**

The system enables end-to-end testing of voice input functionality by:
1. **Generating audio files** from test text using our TTS service
2. **Transcribing audio back to text** using our STT service  
3. **Comparing round-trip accuracy** with similarity scoring
4. **Testing UI components** with generated audio in Playwright

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Test Text     │───▶│  TTS Service    │───▶│   Audio File    │
│ "Hello World"   │    │ (gTTS/OpenAI)   │    │   (.mp3/.wav)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Similarity Test │◀───│ Transcribed Text│◀───│  STT Service    │
│   (85% match)   │    │ "Hello World"   │    │   (Whisper)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Backend services running**: LLM, Whisper-TTS, Database, API
- **Frontend built successfully**: `npm run build` passes
- **TTS service accessible**: `http://localhost:8000/health` returns healthy

### Run Audio Tests

```bash
cd projects/Unhinged/frontend

# Quick demo with standard test cases
npm run test:audio-demo

# Custom test cases (DoorDash, React components, etc.)
npm run test:audio-custom

# Performance benchmark
npm run test:audio-benchmark

# Full test suite
npm run test:audio-all

# Playwright E2E tests with audio
npm run test:audio
```

## 📋 Test Cases

### Standard Test Cases
- **Basic Greeting**: "Hello, this is a basic audio test"
- **Pangram**: "The quick brown fox jumps over the lazy dog"
- **Numbers & Dates**: "Today is January 4th, 2025, temperature is 72 degrees"
- **Voice Commands**: "Create a voice input with submit button"
- **Stock Requests**: "Show me DoorDash stock chart with weekly candles"
- **Technical Terms**: "Initialize React component with TypeScript interfaces"

### Custom Test Cases
- **DoorDash Stock Chart**: Complex financial requests
- **React Components**: Technical programming commands  
- **Voice UI**: Interface generation commands
- **Edge Cases**: Empty text, single words, punctuation

## 🎯 Usage Examples

### Basic Audio Pipeline Test
```typescript
import { AudioPipelineTester } from './utils/audio-pipeline-testing';

const tester = new AudioPipelineTester({
  serviceBaseUrl: 'http://localhost:8000',
  similarityThreshold: 0.85, // 85% accuracy required
});

await tester.initialize();

const result = await tester.runAudioTest({
  id: 'my-test',
  text: 'Create a DoorDash stock chart',
  description: 'Stock chart voice command'
});

console.log(`Similarity: ${result.similarityScore * 100}%`);
console.log(`Passed: ${result.passed}`);
```

### Playwright Integration
```typescript
import { testVoiceInputWithAudio } from './utils/audio-pipeline-testing';

test('voice input with generated audio', async ({ page }) => {
  await page.goto('/');
  
  // Test voice input with generated audio
  await testVoiceInputWithAudio(
    page, 
    'Show me a DoorDash stock chart',
    '[data-testid="voice-input"]'
  );
  
  // Verify UI response
  await expect(page.locator('[data-testid="chat-messages"]'))
    .toContainText('DoorDash');
});
```

## 📊 Test Results

### Similarity Scoring
- **Levenshtein Distance**: Calculates text similarity (0-1 scale)
- **Normalization**: Removes punctuation, normalizes whitespace
- **Threshold**: Configurable pass/fail threshold (default 85%)

### Performance Metrics
- **Generation Time**: TTS audio creation duration
- **Transcription Time**: STT processing duration  
- **Total Round-trip**: Complete pipeline timing
- **Accuracy Rate**: Percentage of tests passing similarity threshold

### Example Output
```
📝 Test: DoorDash Stock Chart Request
🔤 Original Text: "Show me a DoorDash stock chart with weekly candles"
🎤 Transcribed:   "Show me a door dash stock chart with weekly candles"
📊 Similarity:    92.3%
⏱️  Duration:      3,247ms
✅ PASS
```

## 🔧 Configuration

### AudioTestConfig
```typescript
interface AudioTestConfig {
  serviceBaseUrl: string;     // TTS/STT service URL
  audioOutputDir: string;     // Generated audio storage
  language: string;           // TTS language (en, es, fr, etc.)
  similarityThreshold: number; // Pass/fail threshold (0-1)
  timeoutMs: number;          // Request timeout
}
```

### Environment-Specific Settings
- **Development**: Lower threshold (80%), verbose logging
- **CI/CD**: Higher threshold (90%), performance limits
- **Production**: Strict threshold (95%), error monitoring

## 🧪 Test Categories

### 1. Round-Trip Accuracy Tests
- Verify TTS → STT accuracy across different text types
- Test technical terminology, numbers, punctuation
- Validate similarity scoring algorithms

### 2. Performance Tests  
- Measure audio generation speed
- Test concurrent request handling
- Benchmark memory usage and cleanup

### 3. Integration Tests
- Test Playwright voice input simulation
- Verify UI updates after transcription
- Test error handling and recovery

### 4. Edge Case Tests
- Empty text input
- Very long text (>1000 characters)
- Special characters and emojis
- Multiple languages

## 🐛 Troubleshooting

### Common Issues

**Service Not Available**
```bash
# Check service health
curl http://localhost:8000/health

# Check Docker containers
docker ps | grep whisper-tts

# View service logs
docker logs whisper-tts-service
```

**Low Similarity Scores**
- Check audio quality settings
- Verify language configuration
- Test with simpler text first
- Review TTS/STT service versions

**Timeout Errors**
- Increase `timeoutMs` in config
- Check network connectivity
- Monitor service resource usage
- Test with shorter text samples

### Debug Mode
```bash
# Run with debug logging
DEBUG=audio-pipeline npm run test:audio-demo

# Generate audio files without cleanup
npm run test:audio-demo --no-cleanup

# Test specific cases only
npm run test:audio-custom
```

## 📈 Metrics & Monitoring

### Key Performance Indicators
- **Accuracy Rate**: % of tests passing similarity threshold
- **Average Latency**: Mean round-trip time
- **Service Uptime**: TTS/STT service availability
- **Error Rate**: % of failed requests

### Monitoring Integration
- **Sentry**: Error tracking and performance monitoring
- **DataDog**: Service metrics and alerting
- **Custom Dashboards**: Real-time test results

## 🔮 Future Enhancements

### Planned Features
- **Multiple TTS Engines**: OpenAI, Azure, AWS Polly
- **Voice Cloning**: Custom voice models
- **Real-time Testing**: Live audio stream testing
- **A/B Testing**: Compare different TTS/STT combinations
- **Multilingual Support**: Extended language testing
- **Visual Testing**: Waveform analysis and comparison

### Integration Roadmap
- **CI/CD Pipeline**: Automated audio testing in builds
- **Performance Regression**: Historical accuracy tracking
- **Load Testing**: High-volume concurrent audio processing
- **Mobile Testing**: iOS/Android voice input testing

---

## 🎉 Ready to Test!

Your audio pipeline testing system is now fully operational. Run the demo to see it in action:

```bash
npm run test:audio-demo
```

This will generate audio files, transcribe them back to text, and show you the complete round-trip accuracy results! 🚀
