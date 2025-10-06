// ============================================================================
// Audio Domain Service - Pure Business Logic
// ============================================================================
//
// @file AudioDomainService.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Pure business logic for audio processing operations
//
// This service contains the core business rules for audio processing,
// independent of any infrastructure concerns. It defines the contracts
// that infrastructure implementations must fulfill.
//
// Clean Architecture Principles:
// - No external dependencies (no HTTP, database, etc.)
// - Pure business logic only
// - Defines interfaces for infrastructure to implement
// - All operations are deterministic and testable
// ============================================================================

package com.unhinged.domain.audio

import kotlinx.coroutines.flow.Flow

// ============================================================================
// Domain Service Interface
// ============================================================================

/**
 * Core audio processing domain service
 * 
 * Contains pure business logic for audio operations. Infrastructure
 * implementations provide the actual processing capabilities.
 */
interface AudioDomainService {
    
    /**
     * Validates a text-to-speech request
     * 
     * @param synthesis The synthesis request to validate
     * @return List of validation errors (empty if valid)
     */
    fun validateSynthesisRequest(synthesis: AudioSynthesis): List<AudioValidationError>
    
    /**
     * Validates an audio transcription
     * 
     * @param transcription The transcription to validate
     * @return List of validation errors (empty if valid)
     */
    fun validateTranscription(transcription: AudioTranscription): List<AudioValidationError>
    
    /**
     * Calculates estimated cost for audio synthesis
     * 
     * @param synthesis The synthesis request
     * @param voice The voice to be used
     * @return Estimated cost in USD
     */
    fun calculateSynthesisCost(synthesis: AudioSynthesis, voice: Voice): Float
    
    /**
     * Determines optimal audio settings for a given context
     * 
     * @param context The processing context
     * @return Optimized audio options
     */
    fun optimizeAudioSettings(context: AudioProcessingContext): AudioOptions
    
    /**
     * Validates voice compatibility with synthesis request
     * 
     * @param voice The voice to check
     * @param synthesis The synthesis request
     * @return True if compatible, false otherwise
     */
    fun isVoiceCompatible(voice: Voice, synthesis: AudioSynthesis): Boolean
    
    /**
     * Generates audio session metadata
     * 
     * @param sessionType The type of session
     * @param userId The user ID
     * @param context Additional context
     * @return Session metadata map
     */
    fun generateSessionMetadata(
        sessionType: AudioSessionType,
        userId: String,
        context: Map<String, String> = emptyMap()
    ): Map<String, String>
}

// ============================================================================
// Repository Interfaces (Domain Contracts)
// ============================================================================

/**
 * Audio data repository interface
 * 
 * Defines the contract for audio data persistence without
 * specifying implementation details.
 */
interface AudioRepository {
    
    /**
     * Saves an audio transcription
     */
    suspend fun saveTranscription(transcription: AudioTranscription): AudioTranscription
    
    /**
     * Retrieves a transcription by ID
     */
    suspend fun getTranscription(id: String): AudioTranscription?
    
    /**
     * Saves an audio synthesis record
     */
    suspend fun saveSynthesis(synthesis: AudioSynthesis): AudioSynthesis
    
    /**
     * Retrieves a synthesis by ID
     */
    suspend fun getSynthesis(id: String): AudioSynthesis?
    
    /**
     * Lists transcriptions for a user
     */
    suspend fun listTranscriptions(
        userId: String,
        limit: Int = 50,
        offset: Int = 0
    ): List<AudioTranscription>
    
    /**
     * Lists syntheses for a user
     */
    suspend fun listSyntheses(
        userId: String,
        limit: Int = 50,
        offset: Int = 0
    ): List<AudioSynthesis>
    
    /**
     * Deletes a transcription
     */
    suspend fun deleteTranscription(id: String): Boolean
    
    /**
     * Deletes a synthesis
     */
    suspend fun deleteSynthesis(id: String): Boolean
}

/**
 * Voice repository interface
 * 
 * Defines the contract for voice data management.
 */
interface VoiceRepository {
    
    /**
     * Saves a voice definition
     */
    suspend fun saveVoice(voice: Voice): Voice
    
    /**
     * Retrieves a voice by ID
     */
    suspend fun getVoice(id: String): Voice?
    
    /**
     * Lists available voices with filtering
     */
    suspend fun listVoices(
        language: String? = null,
        gender: VoiceGender? = null,
        style: VoiceStyle? = null,
        premiumOnly: Boolean = false,
        limit: Int = 50,
        offset: Int = 0
    ): List<Voice>
    
    /**
     * Searches voices by name or description
     */
    suspend fun searchVoices(query: String, limit: Int = 20): List<Voice>
    
    /**
     * Updates voice availability
     */
    suspend fun updateVoiceAvailability(id: String, isAvailable: Boolean): Boolean
    
    /**
     * Deletes a voice
     */
    suspend fun deleteVoice(id: String): Boolean
}

/**
 * Audio session repository interface
 */
interface AudioSessionRepository {
    
    /**
     * Creates a new audio session
     */
    suspend fun createSession(session: AudioSession): AudioSession
    
    /**
     * Retrieves a session by ID
     */
    suspend fun getSession(id: String): AudioSession?
    
    /**
     * Updates session status
     */
    suspend fun updateSessionStatus(id: String, status: AudioSessionStatus): Boolean
    
    /**
     * Lists sessions for a user
     */
    suspend fun listUserSessions(
        userId: String,
        sessionType: AudioSessionType? = null,
        limit: Int = 50,
        offset: Int = 0
    ): List<AudioSession>
    
    /**
     * Deletes a session
     */
    suspend fun deleteSession(id: String): Boolean
}

// ============================================================================
// Audio Processing Interface (Infrastructure Contract)
// ============================================================================

/**
 * Audio processing service interface
 * 
 * Defines the contract for actual audio processing operations.
 * Infrastructure implementations provide the real processing logic.
 */
interface AudioProcessingService {
    
    /**
     * Converts text to speech with streaming output
     * 
     * @param synthesis The synthesis request
     * @return Flow of audio chunks
     */
    suspend fun synthesizeText(synthesis: AudioSynthesis): Flow<AudioChunk>
    
    /**
     * Converts speech to text from streaming input
     * 
     * @param audioChunks Flow of audio data chunks
     * @param options Processing options
     * @return Transcription result
     */
    suspend fun transcribeAudio(
        audioChunks: Flow<AudioChunk>,
        options: AudioOptions = AudioOptions()
    ): AudioTranscription
    
    /**
     * Processes an audio file (batch operation)
     * 
     * @param audioData The audio file data
     * @param processingType Type of processing to perform
     * @param options Processing options
     * @return Processing result
     */
    suspend fun processAudioFile(
        audioData: ByteArray,
        processingType: AudioProcessingType,
        options: AudioOptions = AudioOptions()
    ): AudioProcessingResult
    
    /**
     * Converts audio between formats
     * 
     * @param audioData Input audio data
     * @param sourceFormat Source audio format
     * @param targetFormat Target audio format
     * @param options Conversion options
     * @return Converted audio data
     */
    suspend fun convertAudioFormat(
        audioData: ByteArray,
        sourceFormat: AudioFormat,
        targetFormat: AudioFormat,
        options: AudioOptions = AudioOptions()
    ): ByteArray
    
    /**
     * Analyzes audio content
     * 
     * @param audioData The audio data to analyze
     * @param analysisTypes Types of analysis to perform
     * @return Analysis results
     */
    suspend fun analyzeAudio(
        audioData: ByteArray,
        analysisTypes: List<AudioAnalysisType>
    ): AudioAnalysisResult
    
    /**
     * Checks if the service is healthy and ready
     */
    suspend fun healthCheck(): AudioServiceHealth
}

// ============================================================================
// Supporting Types
// ============================================================================

/**
 * Audio chunk for streaming operations
 */
data class AudioChunk(
    val data: ByteArray,
    val sequenceNumber: Int,
    val isLast: Boolean = false,
    val metadata: Map<String, String> = emptyMap()
) {
    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false
        other as AudioChunk
        return data.contentEquals(other.data) && 
               sequenceNumber == other.sequenceNumber && 
               isLast == other.isLast
    }

    override fun hashCode(): Int {
        var result = data.contentHashCode()
        result = 31 * result + sequenceNumber
        result = 31 * result + isLast.hashCode()
        return result
    }
}

/**
 * Audio processing context for optimization
 */
data class AudioProcessingContext(
    val deviceType: String,
    val networkCondition: String,
    val userPreferences: Map<String, String> = emptyMap(),
    val qualityRequirement: AudioQuality = AudioQuality.STANDARD
)

/**
 * Audio processing result
 */
sealed class AudioProcessingResult {
    data class TranscriptionResult(val transcription: AudioTranscription) : AudioProcessingResult()
    data class TranslationResult(val translation: String) : AudioProcessingResult()
    data class EnhancementResult(val enhancedAudio: ByteArray) : AudioProcessingResult()
    data class ConversionResult(val convertedAudio: ByteArray) : AudioProcessingResult()
}

/**
 * Audio processing type
 */
enum class AudioProcessingType {
    TRANSCRIBE,
    TRANSLATE,
    ENHANCE,
    CONVERT
}

/**
 * Audio analysis type
 */
enum class AudioAnalysisType {
    SPEECH_DETECTION,
    LANGUAGE_DETECTION,
    SPEAKER_IDENTIFICATION,
    EMOTION_DETECTION,
    QUALITY_ASSESSMENT
}

/**
 * Audio analysis result
 */
data class AudioAnalysisResult(
    val containsSpeech: Boolean,
    val speechPercentage: Float,
    val detectedLanguages: List<String>,
    val speakerCount: Int,
    val emotions: List<String>,
    val qualityScore: Float
)

/**
 * Audio service health status
 */
data class AudioServiceHealth(
    val isHealthy: Boolean,
    val whisperModelLoaded: Boolean,
    val cudaAvailable: Boolean,
    val version: String,
    val capabilities: List<String>
)

/**
 * Audio validation error
 */
data class AudioValidationError(
    val field: String,
    val message: String,
    val code: String
)

// ============================================================================
// Default Domain Service Implementation
// ============================================================================

/**
 * Default implementation of audio domain service
 * 
 * Contains the core business rules and validation logic.
 */
class DefaultAudioDomainService : AudioDomainService {
    
    override fun validateSynthesisRequest(synthesis: AudioSynthesis): List<AudioValidationError> {
        val errors = mutableListOf<AudioValidationError>()
        
        if (synthesis.text.length > 5000) {
            errors.add(AudioValidationError("text", "Text too long (max 5000 characters)", "TEXT_TOO_LONG"))
        }
        
        if (synthesis.text.isBlank()) {
            errors.add(AudioValidationError("text", "Text cannot be blank", "TEXT_BLANK"))
        }
        
        if (synthesis.options.speed !in 0.25f..4.0f) {
            errors.add(AudioValidationError("speed", "Speed must be between 0.25 and 4.0", "INVALID_SPEED"))
        }
        
        return errors
    }
    
    override fun validateTranscription(transcription: AudioTranscription): List<AudioValidationError> {
        val errors = mutableListOf<AudioValidationError>()
        
        if (transcription.confidence < 0.1f) {
            errors.add(AudioValidationError("confidence", "Confidence too low", "LOW_CONFIDENCE"))
        }
        
        if (transcription.segments.isEmpty()) {
            errors.add(AudioValidationError("segments", "No segments found", "NO_SEGMENTS"))
        }
        
        return errors
    }
    
    override fun calculateSynthesisCost(synthesis: AudioSynthesis, voice: Voice): Float {
        val baseRate = if (voice.isPremium) voice.costPerCharacter else 0.001f
        val characterCount = synthesis.text.length
        val qualityMultiplier = when (synthesis.options.quality) {
            AudioQuality.LOW -> 0.8f
            AudioQuality.STANDARD -> 1.0f
            AudioQuality.HIGH -> 1.5f
            AudioQuality.PREMIUM -> 2.0f
            else -> 1.0f
        }
        
        return baseRate * characterCount * qualityMultiplier
    }
    
    override fun optimizeAudioSettings(context: AudioProcessingContext): AudioOptions {
        return when (context.networkCondition) {
            "slow" -> AudioOptions(quality = AudioQuality.LOW)
            "fast" -> AudioOptions(quality = AudioQuality.HIGH)
            else -> AudioOptions(quality = context.qualityRequirement)
        }
    }
    
    override fun isVoiceCompatible(voice: Voice, synthesis: AudioSynthesis): Boolean {
        return voice.isAvailable &&
               voice.supportedFormats.contains(synthesis.outputFormat) &&
               voice.supportedSampleRates.contains(synthesis.sampleRate)
    }
    
    override fun generateSessionMetadata(
        sessionType: AudioSessionType,
        userId: String,
        context: Map<String, String>
    ): Map<String, String> {
        return mapOf(
            "session_type" to sessionType.name,
            "user_id" to userId,
            "created_at" to java.time.Instant.now().toString()
        ) + context
    }
}
