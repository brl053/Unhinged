// ============================================================================
// Audio Domain - Core Business Logic
// ============================================================================
//
// @file AudioDomain.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Core audio domain entities and business logic following proto contracts
//
// This file implements the domain layer for audio processing, strictly following
// the contracts defined in audio.proto. All entities and business rules are
// independent of infrastructure concerns.
//
// Proto Alignment:
// - AudioTranscription maps to STTResponse
// - AudioSynthesis maps to TTSRequest/Response
// - Voice maps to Voice message
// - All enums and types follow proto definitions exactly
// ============================================================================

package com.unhinged.domain.audio

import java.time.Instant
import java.util.*

// ============================================================================
// Core Domain Entities (Proto-Aligned)
// ============================================================================

/**
 * Audio transcription result from speech-to-text processing
 * Maps directly to STTResponse proto message
 */
data class AudioTranscription(
    val id: String = UUID.randomUUID().toString(),
    val transcript: String,
    val confidence: Float,
    val segments: List<TranscriptSegment>,
    val usage: AudioUsage,
    val metadata: STTMetadata,
    val createdAt: Instant = Instant.now()
) {
    init {
        require(transcript.isNotBlank()) { "Transcript cannot be blank" }
        require(confidence in 0.0f..1.0f) { "Confidence must be between 0.0 and 1.0" }
        require(segments.isNotEmpty()) { "Segments cannot be empty" }
    }
}

/**
 * Audio synthesis request and result for text-to-speech processing
 * Maps directly to TTSRequest proto message
 */
data class AudioSynthesis(
    val id: String = UUID.randomUUID().toString(),
    val text: String,
    val voiceId: String,
    val options: AudioOptions,
    val outputFormat: AudioFormat,
    val sampleRate: Int,
    val channels: Int,
    val enableSsml: Boolean = false,
    val effects: List<AudioEffect> = emptyList(),
    val createdAt: Instant = Instant.now()
) {
    init {
        require(text.isNotBlank()) { "Text cannot be blank" }
        require(voiceId.isNotBlank()) { "Voice ID cannot be blank" }
        require(sampleRate > 0) { "Sample rate must be positive" }
        require(channels > 0) { "Channels must be positive" }
    }
}

/**
 * Voice definition for text-to-speech
 * Maps directly to Voice proto message
 */
data class Voice(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val displayName: String,
    val description: String,
    val language: String,
    val languageCode: String,
    val gender: VoiceGender,
    val age: VoiceAge,
    val style: VoiceStyle,
    val supportedFormats: List<AudioFormat>,
    val supportedSampleRates: List<Int>,
    val isAvailable: Boolean = true,
    val isPremium: Boolean = false,
    val costPerCharacter: Float = 0.0f,
    val previewUrl: String? = null,
    val previewText: String? = null,
    val createdAt: Instant = Instant.now()
) {
    init {
        require(name.isNotBlank()) { "Name cannot be blank" }
        require(displayName.isNotBlank()) { "Display name cannot be blank" }
        require(language.isNotBlank()) { "Language cannot be blank" }
        require(languageCode.isNotBlank()) { "Language code cannot be blank" }
        require(supportedFormats.isNotEmpty()) { "Must support at least one format" }
        require(supportedSampleRates.isNotEmpty()) { "Must support at least one sample rate" }
        require(costPerCharacter >= 0.0f) { "Cost per character cannot be negative" }
    }
}

/**
 * Audio processing session for tracking operations
 */
data class AudioSession(
    val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val sessionType: AudioSessionType,
    val status: AudioSessionStatus = AudioSessionStatus.ACTIVE,
    val createdAt: Instant = Instant.now(),
    val updatedAt: Instant = Instant.now(),
    val metadata: Map<String, String> = emptyMap()
) {
    init {
        require(userId.isNotBlank()) { "User ID cannot be blank" }
    }
}

// ============================================================================
// Value Objects (Proto-Aligned)
// ============================================================================

/**
 * Transcript segment with timing information
 * Maps directly to TranscriptSegment proto message
 */
data class TranscriptSegment(
    val text: String,
    val startTime: Float,
    val endTime: Float,
    val confidence: Float,
    val words: List<WordTiming> = emptyList(),
    val speakerId: String? = null
) {
    init {
        require(text.isNotBlank()) { "Segment text cannot be blank" }
        require(startTime >= 0.0f) { "Start time cannot be negative" }
        require(endTime > startTime) { "End time must be after start time" }
        require(confidence in 0.0f..1.0f) { "Confidence must be between 0.0 and 1.0" }
    }
}

/**
 * Word-level timing information
 * Maps directly to WordTiming proto message
 */
data class WordTiming(
    val word: String,
    val startTime: Float,
    val endTime: Float,
    val confidence: Float
) {
    init {
        require(word.isNotBlank()) { "Word cannot be blank" }
        require(startTime >= 0.0f) { "Start time cannot be negative" }
        require(endTime > startTime) { "End time must be after start time" }
        require(confidence in 0.0f..1.0f) { "Confidence must be between 0.0 and 1.0" }
    }
}

/**
 * Audio processing options
 * Maps directly to AudioOptions proto message
 */
data class AudioOptions(
    val speed: Float = 1.0f,
    val pitch: Float = 0.0f,
    val volume: Float = 1.0f,
    val quality: AudioQuality = AudioQuality.STANDARD,
    val enableNoiseReduction: Boolean = false,
    val enableEchoCancellation: Boolean = false
) {
    init {
        require(speed in 0.25f..4.0f) { "Speed must be between 0.25 and 4.0" }
        require(pitch in -20.0f..20.0f) { "Pitch must be between -20 and 20 semitones" }
        require(volume in 0.0f..2.0f) { "Volume must be between 0.0 and 2.0" }
    }
}

/**
 * Audio effect configuration
 * Maps directly to AudioEffect proto message
 */
data class AudioEffect(
    val type: AudioEffectType,
    val intensity: Float,
    val parameters: Map<String, String> = emptyMap()
) {
    init {
        require(intensity in 0.0f..1.0f) { "Intensity must be between 0.0 and 1.0" }
    }
}

/**
 * Audio usage metrics
 * Maps directly to AudioUsage proto message
 */
data class AudioUsage(
    val durationSeconds: Float,
    val bytesProcessed: Long,
    val sampleRate: Int,
    val channels: Int,
    val format: String
) {
    init {
        require(durationSeconds >= 0.0f) { "Duration cannot be negative" }
        require(bytesProcessed >= 0L) { "Bytes processed cannot be negative" }
        require(sampleRate > 0) { "Sample rate must be positive" }
        require(channels > 0) { "Channels must be positive" }
        require(format.isNotBlank()) { "Format cannot be blank" }
    }
}

/**
 * STT processing metadata
 * Maps directly to STTMetadata proto message
 */
data class STTMetadata(
    val model: String,
    val language: String,
    val processingTimeMs: Float,
    val signalToNoiseRatio: Float,
    val speechRateWpm: Float,
    val detectedLanguages: List<String>,
    val hasBackgroundNoise: Boolean,
    val hasMultipleSpeakers: Boolean,
    val detectedQuality: AudioQuality
) {
    init {
        require(model.isNotBlank()) { "Model cannot be blank" }
        require(language.isNotBlank()) { "Language cannot be blank" }
        require(processingTimeMs >= 0.0f) { "Processing time cannot be negative" }
        require(speechRateWpm >= 0.0f) { "Speech rate cannot be negative" }
    }
}

// ============================================================================
// Enums (Proto-Aligned)
// ============================================================================

/**
 * Audio quality levels
 * Maps directly to AudioQuality proto enum
 */
enum class AudioQuality {
    UNSPECIFIED,
    LOW,        // 16kHz, compressed
    STANDARD,   // 22kHz, balanced
    HIGH,       // 44kHz, high quality
    PREMIUM     // 48kHz, studio quality
}

/**
 * Audio format specification
 * Maps directly to AudioFormat proto enum
 */
enum class AudioFormat {
    UNSPECIFIED,
    WAV,        // Uncompressed WAV
    MP3,        // MP3 compressed
    OGG,        // OGG Vorbis
    FLAC,       // Lossless FLAC
    PCM,        // Raw PCM data
    OPUS,       // Opus codec (low latency)
    AAC         // AAC compressed
}

/**
 * Audio effects that can be applied
 * Maps directly to AudioEffectType proto enum
 */
enum class AudioEffectType {
    UNSPECIFIED,
    REVERB,
    ECHO,
    CHORUS,
    DISTORTION,
    NORMALIZE,
    COMPRESSOR
}

/**
 * Voice gender classification
 * Maps directly to VoiceGender proto enum
 */
enum class VoiceGender {
    UNSPECIFIED,
    MALE,
    FEMALE,
    NEUTRAL,
    CHILD
}

/**
 * Voice age classification
 * Maps directly to VoiceAge proto enum
 */
enum class VoiceAge {
    UNSPECIFIED,
    CHILD,          // Under 18
    YOUNG_ADULT,    // 18-30
    ADULT,          // 30-50
    SENIOR          // Over 50
}

/**
 * Voice style and personality
 * Maps directly to VoiceStyle proto enum
 */
enum class VoiceStyle {
    UNSPECIFIED,
    CONVERSATIONAL,     // Natural, casual
    PROFESSIONAL,       // Business, formal
    FRIENDLY,           // Warm, approachable
    AUTHORITATIVE,      // Confident, commanding
    CALM,               // Soothing, relaxed
    ENERGETIC,          // Upbeat, enthusiastic
    DRAMATIC            // Expressive, theatrical
}

/**
 * Audio session type
 */
enum class AudioSessionType {
    TEXT_TO_SPEECH,
    SPEECH_TO_TEXT,
    AUDIO_PROCESSING,
    VOICE_TRAINING
}

/**
 * Audio session status
 */
enum class AudioSessionStatus {
    ACTIVE,
    COMPLETED,
    FAILED,
    CANCELLED
}
