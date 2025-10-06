#!/usr/bin/env node

// Test Event Feed - Simulate events to test the real-time event feed
// This script sends various events to the Event API to test the live feed

const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const EVENT_API_URL = 'http://localhost:8084/events';

// Test events to simulate different scenarios
const testEvents = [
  {
    type: 'voice_recording_started',
    source: 'voice-recorder',
    data: {
      sessionId: 'demo-session-123',
      audioFormat: 'webm'
    }
  },
  {
    type: 'voice_recording_stopped',
    source: 'voice-recorder',
    data: {
      sessionId: 'demo-session-123',
      duration: 3500,
      audioSize: 28420,
      audioFormat: 'webm'
    }
  },
  {
    type: 'transcription_started',
    source: 'whisper-tts',
    data: {
      sessionId: 'demo-session-123',
      audioSize: 28420
    }
  },
  {
    type: 'transcription_completed',
    source: 'whisper-tts',
    data: {
      sessionId: 'demo-session-123',
      audioSize: 28420,
      transcriptionText: 'Hello, this is a test voice message for the event feed',
      language: 'en',
      confidence: 0.97,
      processingTimeMs: 1850
    }
  },
  {
    type: 'chat_message_sent',
    source: 'react-frontend',
    data: {
      sessionId: 'demo-session-123',
      messageContent: 'Hello, this is a test voice message for the event feed',
      messageRole: 'user',
      messageSource: 'voice'
    }
  },
  {
    type: 'chat_message_received',
    source: 'react-frontend',
    data: {
      sessionId: 'demo-session-123',
      messageContent: 'I received your voice message! The transcription worked perfectly.',
      messageRole: 'assistant',
      processingTimeMs: 450
    }
  }
];

async function sendTestEvent(event, delay = 1000) {
  const eventWithMetadata = {
    id: `test_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date().toISOString(),
    metadata: {
      testRun: true,
      sessionId: event.data.sessionId
    },
    version: '1.0.0',
    ...event
  };

  try {
    console.log(`📤 Sending: ${event.type} (${event.source})`);
    
    const response = await fetch(EVENT_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify([eventWithMetadata])
    });

    if (response.ok) {
      const result = await response.json();
      console.log(`✅ Persisted: ${event.type} (${result.persisted}/${result.processed})`);
    } else {
      console.log(`❌ Failed: ${event.type} - HTTP ${response.status}`);
    }
  } catch (error) {
    console.log(`❌ Error: ${event.type} - ${error.message}`);
  }

  // Wait before next event
  if (delay > 0) {
    await new Promise(resolve => setTimeout(resolve, delay));
  }
}

async function runEventFeedTest() {
  console.log('🎯 Testing Real-Time Event Feed');
  console.log('===============================');
  console.log('This will simulate a complete voice recording flow');
  console.log('Watch the events appear in the React app at http://localhost:8081');
  console.log('');

  // Send events with realistic timing
  for (let i = 0; i < testEvents.length; i++) {
    const event = testEvents[i];
    const delay = i < testEvents.length - 1 ? 2000 : 0; // 2 second delay between events
    await sendTestEvent(event, delay);
  }

  console.log('');
  console.log('🎉 Event feed test complete!');
  console.log('Check the React app to see the live events in the chat window');
  console.log('');
  console.log('💡 You can also check the database:');
  console.log('   node db-debug.js debug');
}

// Run the test
if (require.main === module) {
  runEventFeedTest().catch(console.error);
}
