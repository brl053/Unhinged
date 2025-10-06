// ============================================================================
// Whisper TTS Client - Infrastructure Layer
// ============================================================================
//
// @file WhisperTtsClient.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description HTTP client for Whisper TTS Python service integration
//
// This client implements the AudioProcessingService interface by communicating
// with the Python Flask/gRPC service. It handles the translation between
// domain objects and the external service API.
//
// Clean Architecture:
// - Implements domain AudioProcessingService interface
// - Handles external service communication
// - Maps between domain objects and external API
// - Provides error handling and resilience
// ============================================================================

package com.unhinged.infrastructure.audio

import com.unhinged.domain.audio.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.collect
import kotlinx.serialization.*
import kotlinx.serialization.json.Json
import java.io.ByteArrayOutputStream
import java.time.Instant

// ============================================================================
// Whisper TTS Client Implementation
// ============================================================================

/**
 * HTTP client implementation for Whisper TTS service
 * 
 * Communicates with the Python Flask service to provide actual audio processing.
 * Maps domain objects to/from the external service API.
 */
class WhisperTtsClient(
    private val configuration: AudioConfiguration
) : AudioProcessingService {
    
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
            })
        }
    }
    
    override suspend fun synthesizeText(synthesis: AudioSynthesis): Flow<AudioChunk> = flow {
        try {
            val request = TtsRequest(
                text = synthesis.text,
                language = extractLanguageFromVoiceId(synthesis.voiceId)
            )
            
            val response: HttpResponse = client.post("${configuration.whisperTtsHost}/synthesize") {
                contentType(ContentType.Application.Json)
                setBody(request)
            }
            
            if (!response.status.isSuccess()) {
                val errorBody = response.bodyAsText()
                throw AudioProcessingException("TTS service error: ${response.status.value} - $errorBody")
            }
            
            // Get the audio bytes
            val audioBytes = response.body<ByteArray>()
            
            // For now, emit as a single chunk
            // In a real streaming implementation, we'd chunk the data
            emit(AudioChunk(
                data = audioBytes,
                sequenceNumber = 1,
                isLast = true,
                metadata = mapOf(
                    "format" to synthesis.outputFormat.name,
                    "sample_rate" to synthesis.sampleRate.toString(),
                    "channels" to synthesis.channels.toString()
                )
            ))
            
        } catch (e: Exception) {
            throw AudioProcessingException("Failed to synthesize speech: ${e.message}", e)
        }
    }
    
    override suspend fun transcribeAudio(
        audioChunks: Flow<AudioChunk>,
        options: AudioOptions
    ): AudioTranscription {
        try {
            // Collect all audio chunks into a single byte array
            val audioData = ByteArrayOutputStream()
            var totalChunks = 0
            
            audioChunks.collect { chunk ->
                audioData.write(chunk.data)
                totalChunks++
            }
            
            val audioBytes = audioData.toByteArray()
            
            // Create multipart request for file upload
            val response: HttpResponse = client.post("${configuration.whisperTtsHost}/transcribe") {
                setBody(MultiPartFormDataContent(
                    formData {
                        append("audio", audioBytes, Headers.build {
                            append(HttpHeaders.ContentType, "audio/wav")
                            append(HttpHeaders.ContentDisposition, "filename=\"audio.wav\"")
                        })
                    }
                ))
            }
            
            if (!response.status.isSuccess()) {
                val errorBody = response.bodyAsText()
                throw AudioProcessingException("STT service error: ${response.status.value} - $errorBody")
            }
            
            val sttResponse = response.body<SttResponse>()
            
            // Map external response to domain object
            return AudioTranscription(
                transcript = sttResponse.text,
                confidence = 0.9f, // Whisper doesn't provide confidence, use default
                segments = listOf(
                    TranscriptSegment(
                        text = sttResponse.text,
                        startTime = 0.0f,
                        endTime = calculateDuration(audioBytes),
                        confidence = 0.9f
                    )
                ),
                usage = AudioUsage(
                    durationSeconds = calculateDuration(audioBytes),
                    bytesProcessed = audioBytes.size.toLong(),
                    sampleRate = 16000, // Default sample rate
                    channels = 1, // Default mono
                    format = "wav"
                ),
                metadata = STTMetadata(
                    model = "whisper-base",
                    language = sttResponse.language ?: "en",
                    processingTimeMs = 0.0f, // Not provided by service
                    signalToNoiseRatio = 0.0f,
                    speechRateWpm = 0.0f,
                    detectedLanguages = listOfNotNull(sttResponse.language),
                    hasBackgroundNoise = false,
                    hasMultipleSpeakers = false,
                    detectedQuality = AudioQuality.STANDARD
                )
            )
            
        } catch (e: Exception) {
            throw AudioProcessingException("Failed to transcribe audio: ${e.message}", e)
        }
    }
    
    override suspend fun processAudioFile(
        audioData: ByteArray,
        processingType: AudioProcessingType,
        options: AudioOptions
    ): AudioProcessingResult {
        return when (processingType) {
            AudioProcessingType.TRANSCRIBE -> {
                // Convert to flow and transcribe
                val audioFlow = flow {
                    emit(AudioChunk(audioData, 1, true))
                }
                val transcription = transcribeAudio(audioFlow, options)
                AudioProcessingResult.TranscriptionResult(transcription)
            }
            AudioProcessingType.TRANSLATE -> {
                // Not implemented yet
                throw NotImplementedError("Translation not yet implemented")
            }
            AudioProcessingType.ENHANCE -> {
                // Not implemented yet
                throw NotImplementedError("Audio enhancement not yet implemented")
            }
            AudioProcessingType.CONVERT -> {
                // Not implemented yet
                throw NotImplementedError("Audio conversion not yet implemented")
            }
        }
    }
    
    override suspend fun convertAudioFormat(
        audioData: ByteArray,
        sourceFormat: AudioFormat,
        targetFormat: AudioFormat,
        options: AudioOptions
    ): ByteArray {
        // Not implemented yet - would require additional service endpoints
        throw NotImplementedError("Audio format conversion not yet implemented")
    }
    
    override suspend fun analyzeAudio(
        audioData: ByteArray,
        analysisTypes: List<AudioAnalysisType>
    ): AudioAnalysisResult {
        // Not implemented yet - would require additional service endpoints
        throw NotImplementedError("Audio analysis not yet implemented")
    }
    
    override suspend fun healthCheck(): AudioServiceHealth {
        try {
            val response: HttpResponse = client.get("${configuration.whisperTtsHost}/health")
            
            if (!response.status.isSuccess()) {
                return AudioServiceHealth(
                    isHealthy = false,
                    whisperModelLoaded = false,
                    cudaAvailable = false,
                    version = "unknown",
                    capabilities = emptyList()
                )
            }
            
            val healthResponse = response.body<TtsHealthResponse>()
            
            return AudioServiceHealth(
                isHealthy = healthResponse.status == "healthy",
                whisperModelLoaded = healthResponse.whisper_model_loaded,
                cudaAvailable = healthResponse.cuda_available,
                version = healthResponse.version,
                capabilities = healthResponse.capabilities
            )
            
        } catch (e: Exception) {
            return AudioServiceHealth(
                isHealthy = false,
                whisperModelLoaded = false,
                cudaAvailable = false,
                version = "unknown",
                capabilities = emptyList()
            )
        }
    }
    
    // ============================================================================
    // Helper Functions
    // ============================================================================
    
    /**
     * Extracts language code from voice ID
     * This is a simple implementation - in production, you'd look up the voice
     */
    private fun extractLanguageFromVoiceId(voiceId: String): String {
        return when {
            voiceId.contains("en-us", ignoreCase = true) -> "en"
            voiceId.contains("en-gb", ignoreCase = true) -> "en"
            voiceId.contains("es", ignoreCase = true) -> "es"
            voiceId.contains("fr", ignoreCase = true) -> "fr"
            voiceId.contains("de", ignoreCase = true) -> "de"
            else -> "en" // Default to English
        }
    }
    
    /**
     * Calculates approximate duration from audio bytes
     * This is a rough estimate - real implementation would parse audio headers
     */
    private fun calculateDuration(audioBytes: ByteArray): Float {
        // Rough estimate: assume 16kHz, 16-bit, mono
        val bytesPerSecond = 16000 * 2 * 1 // sample_rate * bytes_per_sample * channels
        return audioBytes.size.toFloat() / bytesPerSecond
    }
}

// ============================================================================
// External Service DTOs
// ============================================================================

/**
 * Request DTO for TTS service
 */
@Serializable
data class TtsRequest(
    val text: String,
    val language: String = "en"
)

/**
 * Response DTO from STT service
 */
@Serializable
data class SttResponse(
    val text: String,
    val language: String? = null
)

/**
 * Health check response from TTS service
 */
@Serializable
data class TtsHealthResponse(
    val status: String,
    val whisper_model_loaded: Boolean,
    val cuda_available: Boolean,
    val service: String,
    val version: String,
    val capabilities: List<String>
)

// ============================================================================
// Configuration
// ============================================================================

/**
 * Configuration for audio processing
 */
data class AudioConfiguration(
    val whisperTtsHost: String = "http://localhost:8000",
    val defaultLanguage: String = "en",
    val maxAudioDurationSeconds: Int = 300, // 5 minutes
    val supportedFormats: List<String> = listOf("wav", "mp3", "m4a"),
    val requestTimeoutMs: Long = 30000 // 30 seconds
)
