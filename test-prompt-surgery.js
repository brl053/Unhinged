#!/usr/bin/env node

// Test Prompt Surgery Panel - Simulate voice transcription to surgery panel flow
// This script demonstrates the complete prompt surgery workflow

const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

const EVENT_API_URL = 'http://localhost:8084/events';

// Simulate a complete prompt surgery workflow
const promptSurgeryWorkflow = [
  {
    type: 'voice_recording_started',
    source: 'voice-recorder',
    data: {
      sessionId: 'surgery-demo-session',
      audioFormat: 'webm'
    }
  },
  {
    type: 'voice_recording_stopped',
    source: 'voice-recorder',
    data: {
      sessionId: 'surgery-demo-session',
      duration: 4200,
      audioSize: 33840,
      audioFormat: 'webm'
    }
  },
  {
    type: 'transcription_started',
    source: 'whisper-tts',
    data: {
      sessionId: 'surgery-demo-session',
      audioSize: 33840
    }
  },
  {
    type: 'transcription_completed',
    source: 'whisper-tts',
    data: {
      sessionId: 'surgery-demo-session',
      audioSize: 33840,
      transcriptionText: 'Can you help me understand the difference between machine learning and artificial intelligence?',
      language: 'en',
      confidence: 0.94,
      processingTimeMs: 2100
    }
  },
  {
    type: 'voice_transcription_captured',
    source: 'voice-recorder',
    data: {
      transcriptionText: 'Can you help me understand the difference between machine learning and artificial intelligence?',
      routedToSurgery: true
    }
  },
  {
    type: 'prompt_surgery_started',
    source: 'prompt-surgery-panel',
    data: {
      sourceCount: 1,
      initialLength: 95
    }
  },
  {
    type: 'prompt_source_added',
    source: 'prompt-surgery-panel',
    data: {
      sourceType: 'manual',
      sourceCount: 2
    }
  },
  {
    type: 'prompt_enhancement_started',
    source: 'prompt-surgery-panel',
    data: {
      originalLength: 95,
      sourceCount: 2
    }
  },
  {
    type: 'prompt_enhancement_completed',
    source: 'prompt-surgery-panel',
    data: {
      originalLength: 95,
      enhancedLength: 287,
      processingTimeMs: 1500
    }
  },
  {
    type: 'prompt_surgery_completed',
    source: 'prompt-surgery-panel',
    data: {
      finalLength: 287,
      sourceCount: 3,
      wordCount: 48
    }
  },
  {
    type: 'prompt_surgery_sent',
    source: 'prompt-surgery-panel',
    data: {
      finalPromptLength: 287,
      sourceCount: 3,
      messageSource: 'surgery'
    }
  },
  {
    type: 'chat_message_sent',
    source: 'react-frontend',
    data: {
      sessionId: 'surgery-demo-session',
      messageContent: 'Context: This appears to be a user query about AI/ML concepts that could benefit from structured explanation...',
      messageRole: 'user',
      messageSource: 'surgery'
    }
  },
  {
    type: 'chat_message_received',
    source: 'react-frontend',
    data: {
      sessionId: 'surgery-demo-session',
      messageContent: 'Great question! Machine Learning is actually a subset of Artificial Intelligence. Let me break this down...',
      messageRole: 'assistant',
      processingTimeMs: 850
    }
  }
];

async function sendWorkflowEvent(event, delay = 1000) {
  const eventWithMetadata = {
    id: `surgery_demo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: new Date().toISOString(),
    metadata: {
      demoRun: true,
      workflowType: 'prompt_surgery',
      sessionId: event.data.sessionId || 'surgery-demo-session'
    },
    version: '1.0.0',
    ...event
  };

  try {
    console.log(`📤 ${event.type} (${event.source})`);
    
    const response = await fetch(EVENT_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify([eventWithMetadata])
    });

    if (response.ok) {
      const result = await response.json();
      console.log(`✅ Persisted: ${result.persisted}/${result.processed}`);
    } else {
      console.log(`❌ Failed: HTTP ${response.status}`);
    }
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }

  // Wait before next event
  if (delay > 0) {
    await new Promise(resolve => setTimeout(resolve, delay));
  }
}

async function runPromptSurgeryDemo() {
  console.log('🔧 Prompt Surgery Panel Demo');
  console.log('=============================');
  console.log('This simulates the complete prompt surgery workflow:');
  console.log('1. Voice recording and transcription');
  console.log('2. Routing to surgery panel instead of direct chat');
  console.log('3. Multi-source content stitching');
  console.log('4. Prompt enhancement via backend APIs');
  console.log('5. Final prompt crafting and submission');
  console.log('');
  console.log('🎯 Watch the events in the React app at http://localhost:8081');
  console.log('');

  // Send events with realistic timing
  for (let i = 0; i < promptSurgeryWorkflow.length; i++) {
    const event = promptSurgeryWorkflow[i];
    let delay = 1500; // Default delay
    
    // Adjust timing for realistic flow
    if (event.type.includes('recording')) delay = 500;
    if (event.type.includes('transcription')) delay = 2000;
    if (event.type.includes('enhancement')) delay = 3000;
    if (event.type.includes('surgery')) delay = 1000;
    
    // No delay after last event
    if (i === promptSurgeryWorkflow.length - 1) delay = 0;
    
    await sendWorkflowEvent(event, delay);
  }

  console.log('');
  console.log('🎉 Prompt Surgery Demo Complete!');
  console.log('');
  console.log('📊 Workflow Summary:');
  console.log('   • Voice recording captured and transcribed');
  console.log('   • Transcription routed to Surgery Panel (not direct chat)');
  console.log('   • Manual content sources added');
  console.log('   • Prompt enhanced with backend context');
  console.log('   • Final crafted prompt sent to chat');
  console.log('   • AI response generated');
  console.log('');
  console.log('🔍 Check the database for all events:');
  console.log('   node db-debug.js debug');
  console.log('');
  console.log('🎯 Key Innovation: Voice transcriptions no longer auto-send!');
  console.log('   Users now have full control over prompt crafting before submission.');
}

// Run the demo
if (require.main === module) {
  runPromptSurgeryDemo().catch(console.error);
}
