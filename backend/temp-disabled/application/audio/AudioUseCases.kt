// ============================================================================
// Audio Use Cases - Application Layer
// ============================================================================
//
// @file AudioUseCases.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Application layer use cases for audio processing operations
//
// This layer orchestrates domain objects and coordinates with infrastructure.
// It implements the business workflows defined in the proto contracts while
// maintaining clean architecture principles.
//
// Proto Alignment:
// - TextToSpeechUseCase implements TTSRequest -> StreamChunk flow
// - SpeechToTextUseCase implements StreamChunk flow -> STTResponse
// - All operations follow proto-defined request/response patterns
// ============================================================================

package com.unhinged.application.audio

import com.unhinged.domain.audio.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onEach
import java.time.Instant

// Generated proto imports
import unhinged.audio.TTSRequest
import unhinged.audio.STTResponse
import unhinged.audio.AudioOptions as AudioOptionsProto
import unhinged.audio.AudioEffect as AudioEffectProto
import unhinged.audio.AudioQuality as AudioQualityProto
import unhinged.audio.AudioEffectType as AudioEffectTypeProto
import unhinged.common.StreamChunk

// ============================================================================
// Text-to-Speech Use Case
// ============================================================================

/**
 * Text-to-Speech use case
 * 
 * Orchestrates the conversion of text to speech following clean architecture.
 * Maps proto TTSRequest to domain objects and coordinates processing.
 */
class TextToSpeechUseCase(
    private val audioProcessingService: AudioProcessingService,
    private val voiceRepository: VoiceRepository,
    private val audioRepository: AudioRepository,
    private val sessionRepository: AudioSessionRepository,
    private val domainService: AudioDomainService
) {
    
    /**
     * Executes text-to-speech conversion with streaming output
     * 
     * @param request The TTS request (proto-aligned)
     * @param userId The requesting user ID
     * @return Flow of audio chunks for streaming
     */
    suspend fun execute(request: TTSRequest, userId: String): Flow<AudioChunk> {
        // Create domain objects from request
        val synthesis = AudioSynthesis(
            text = request.text,
            voiceId = request.voiceId,
            options = request.options.toDomain(),
            outputFormat = request.outputFormat,
            sampleRate = request.sampleRate,
            channels = request.channels,
            enableSsml = request.enableSsml,
            effects = request.effects.map { it.toDomain() }
        )
        
        // Validate the request
        val validationErrors = domainService.validateSynthesisRequest(synthesis)
        if (validationErrors.isNotEmpty()) {
            throw AudioValidationException("Invalid synthesis request", validationErrors)
        }
        
        // Get and validate voice
        val voice = voiceRepository.getVoice(request.voiceId)
            ?: throw AudioNotFoundException("Voice not found: ${request.voiceId}")
        
        if (!domainService.isVoiceCompatible(voice, synthesis)) {
            throw AudioIncompatibilityException("Voice not compatible with request parameters")
        }
        
        // Create session for tracking
        val session = AudioSession(
            userId = userId,
            sessionType = AudioSessionType.TEXT_TO_SPEECH,
            metadata = domainService.generateSessionMetadata(
                AudioSessionType.TEXT_TO_SPEECH,
                userId,
                mapOf(
                    "voice_id" to request.voiceId,
                    "text_length" to request.text.length.toString(),
                    "output_format" to request.outputFormat.name
                )
            )
        )
        
        val createdSession = sessionRepository.createSession(session)
        
        return flow {
            try {
                // Save synthesis record
                val savedSynthesis = audioRepository.saveSynthesis(synthesis)
                
                // Process with infrastructure service
                audioProcessingService.synthesizeText(savedSynthesis)
                    .onEach { chunk ->
                        // Emit each chunk as it's processed
                        emit(chunk)
                    }
                    .collect { chunk ->
                        // Final chunk processing if needed
                        if (chunk.isLast) {
                            sessionRepository.updateSessionStatus(
                                createdSession.id,
                                AudioSessionStatus.COMPLETED
                            )
                        }
                    }
                    
            } catch (e: Exception) {
                sessionRepository.updateSessionStatus(
                    createdSession.id,
                    AudioSessionStatus.FAILED
                )
                throw AudioProcessingException("TTS processing failed", e)
            }
        }
    }
}

// ============================================================================
// Speech-to-Text Use Case
// ============================================================================

/**
 * Speech-to-Text use case
 * 
 * Orchestrates the conversion of speech to text following clean architecture.
 * Maps proto StreamChunk flow to domain objects and coordinates processing.
 */
class SpeechToTextUseCase(
    private val audioProcessingService: AudioProcessingService,
    private val audioRepository: AudioRepository,
    private val sessionRepository: AudioSessionRepository,
    private val domainService: AudioDomainService
) {
    
    /**
     * Executes speech-to-text conversion from streaming input
     * 
     * @param audioChunks Flow of audio data chunks
     * @param userId The requesting user ID
     * @param options Processing options
     * @return Transcription result
     */
    suspend fun execute(
        audioChunks: Flow<AudioChunk>,
        userId: String,
        options: AudioOptions = AudioOptions()
    ): AudioTranscription {
        
        // Create session for tracking
        val session = AudioSession(
            userId = userId,
            sessionType = AudioSessionType.SPEECH_TO_TEXT,
            metadata = domainService.generateSessionMetadata(
                AudioSessionType.SPEECH_TO_TEXT,
                userId,
                mapOf(
                    "quality" to options.quality.name,
                    "noise_reduction" to options.enableNoiseReduction.toString()
                )
            )
        )
        
        val createdSession = sessionRepository.createSession(session)
        
        return try {
            // Process with infrastructure service
            val transcription = audioProcessingService.transcribeAudio(audioChunks, options)
            
            // Validate the result
            val validationErrors = domainService.validateTranscription(transcription)
            if (validationErrors.isNotEmpty()) {
                throw AudioValidationException("Invalid transcription result", validationErrors)
            }
            
            // Save transcription
            val savedTranscription = audioRepository.saveTranscription(transcription)
            
            // Update session status
            sessionRepository.updateSessionStatus(createdSession.id, AudioSessionStatus.COMPLETED)
            
            savedTranscription
            
        } catch (e: Exception) {
            sessionRepository.updateSessionStatus(createdSession.id, AudioSessionStatus.FAILED)
            throw AudioProcessingException("STT processing failed", e)
        }
    }
}

// ============================================================================
// Voice Management Use Case
// ============================================================================

/**
 * Voice management use case
 * 
 * Handles voice-related operations like listing, getting, and managing voices.
 */
class VoiceManagementUseCase(
    private val voiceRepository: VoiceRepository,
    private val domainService: AudioDomainService
) {
    
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
    ): List<Voice> {
        return voiceRepository.listVoices(language, gender, style, premiumOnly, limit, offset)
    }
    
    /**
     * Gets a specific voice by ID
     */
    suspend fun getVoice(voiceId: String): Voice {
        return voiceRepository.getVoice(voiceId)
            ?: throw AudioNotFoundException("Voice not found: $voiceId")
    }
    
    /**
     * Searches voices by query
     */
    suspend fun searchVoices(query: String, limit: Int = 20): List<Voice> {
        return voiceRepository.searchVoices(query, limit)
    }
    
    /**
     * Creates a custom voice (placeholder for future implementation)
     */
    suspend fun createCustomVoice(
        name: String,
        description: String,
        trainingSamples: List<ByteArray>,
        targetGender: VoiceGender,
        targetStyle: VoiceStyle,
        userId: String
    ): Voice {
        // This would involve complex voice training logic
        // For now, return a placeholder implementation
        throw NotImplementedError("Custom voice creation not yet implemented")
    }
}

// ============================================================================
// Audio File Processing Use Case
// ============================================================================

/**
 * Audio file processing use case
 * 
 * Handles batch processing of audio files for various operations.
 */
class ProcessAudioFileUseCase(
    private val audioProcessingService: AudioProcessingService,
    private val audioRepository: AudioRepository,
    private val sessionRepository: AudioSessionRepository,
    private val domainService: AudioDomainService
) {
    
    /**
     * Processes an audio file based on the specified processing type
     */
    suspend fun execute(
        audioData: ByteArray,
        processingType: AudioProcessingType,
        options: AudioOptions,
        userId: String
    ): AudioProcessingResult {
        
        // Create session for tracking
        val session = AudioSession(
            userId = userId,
            sessionType = AudioSessionType.AUDIO_PROCESSING,
            metadata = domainService.generateSessionMetadata(
                AudioSessionType.AUDIO_PROCESSING,
                userId,
                mapOf(
                    "processing_type" to processingType.name,
                    "audio_size" to audioData.size.toString()
                )
            )
        )
        
        val createdSession = sessionRepository.createSession(session)
        
        return try {
            val result = audioProcessingService.processAudioFile(audioData, processingType, options)
            
            // Save result if it's a transcription
            if (result is AudioProcessingResult.TranscriptionResult) {
                audioRepository.saveTranscription(result.transcription)
            }
            
            sessionRepository.updateSessionStatus(createdSession.id, AudioSessionStatus.COMPLETED)
            result
            
        } catch (e: Exception) {
            sessionRepository.updateSessionStatus(createdSession.id, AudioSessionStatus.FAILED)
            throw AudioProcessingException("Audio file processing failed", e)
        }
    }
}

// ============================================================================
// Extension Functions for Proto Mapping
// ============================================================================

/**
 * Converts proto AudioOptions to domain AudioOptions
 */
private fun AudioOptionsProto.toDomain(): AudioOptions {
    return AudioOptions(
        speed = this.speed,
        pitch = this.pitch,
        volume = this.volume,
        quality = this.quality.toDomain(),
        enableNoiseReduction = this.enableNoiseReduction,
        enableEchoCancellation = this.enableEchoCancellation
    )
}

/**
 * Converts proto AudioQuality to domain AudioQuality
 */
private fun AudioQualityProto.toDomain(): AudioQuality {
    return when (this) {
        AudioQualityProto.AUDIO_QUALITY_LOW -> AudioQuality.LOW
        AudioQualityProto.AUDIO_QUALITY_STANDARD -> AudioQuality.STANDARD
        AudioQualityProto.AUDIO_QUALITY_HIGH -> AudioQuality.HIGH
        AudioQualityProto.AUDIO_QUALITY_PREMIUM -> AudioQuality.PREMIUM
        else -> AudioQuality.STANDARD
    }
}

/**
 * Converts proto AudioEffect to domain AudioEffect
 */
private fun AudioEffectProto.toDomain(): AudioEffect {
    return AudioEffect(
        type = this.type.toDomain(),
        intensity = this.intensity,
        parameters = this.parametersMap
    )
}

/**
 * Converts proto AudioEffectType to domain AudioEffectType
 */
private fun AudioEffectTypeProto.toDomain(): AudioEffectType {
    return when (this) {
        AudioEffectTypeProto.AUDIO_EFFECT_TYPE_REVERB -> AudioEffectType.REVERB
        AudioEffectTypeProto.AUDIO_EFFECT_TYPE_ECHO -> AudioEffectType.ECHO
        AudioEffectTypeProto.AUDIO_EFFECT_TYPE_CHORUS -> AudioEffectType.CHORUS
        AudioEffectTypeProto.AUDIO_EFFECT_TYPE_DISTORTION -> AudioEffectType.DISTORTION
        AudioEffectTypeProto.AUDIO_EFFECT_TYPE_NORMALIZE -> AudioEffectType.NORMALIZE
        AudioEffectTypeProto.AUDIO_EFFECT_TYPE_COMPRESSOR -> AudioEffectType.COMPRESSOR
        else -> AudioEffectType.UNSPECIFIED
    }
}

// ============================================================================
// Exception Types
// ============================================================================

/**
 * Base exception for audio processing errors
 */
sealed class AudioException(message: String, cause: Throwable? = null) : Exception(message, cause)

/**
 * Validation exception for invalid requests
 */
class AudioValidationException(
    message: String,
    val errors: List<AudioValidationError>
) : AudioException(message)

/**
 * Not found exception for missing resources
 */
class AudioNotFoundException(message: String) : AudioException(message)

/**
 * Incompatibility exception for mismatched parameters
 */
class AudioIncompatibilityException(message: String) : AudioException(message)

/**
 * Processing exception for infrastructure failures
 */
class AudioProcessingException(message: String, cause: Throwable? = null) : AudioException(message, cause)

// ============================================================================
// Proto Mapping Extensions (Updated for Generated Types)
// ============================================================================

/**
 * Converts proto AudioFormat to domain AudioFormat
 */
private fun unhinged.audio.AudioFormat.toDomain(): AudioFormat {
    return when (this) {
        unhinged.audio.AudioFormat.AUDIO_FORMAT_WAV -> AudioFormat.WAV
        unhinged.audio.AudioFormat.AUDIO_FORMAT_MP3 -> AudioFormat.MP3
        unhinged.audio.AudioFormat.AUDIO_FORMAT_OGG -> AudioFormat.OGG
        unhinged.audio.AudioFormat.AUDIO_FORMAT_FLAC -> AudioFormat.FLAC
        unhinged.audio.AudioFormat.AUDIO_FORMAT_PCM -> AudioFormat.PCM
        unhinged.audio.AudioFormat.AUDIO_FORMAT_OPUS -> AudioFormat.OPUS
        unhinged.audio.AudioFormat.AUDIO_FORMAT_AAC -> AudioFormat.AAC
        else -> AudioFormat.UNSPECIFIED
    }
}
