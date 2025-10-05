// ============================================================================
// Whisper TTS gRPC Client - Infrastructure Layer
// ============================================================================
//
// @file WhisperTtsGrpcClient.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description gRPC client for Whisper TTS service integration
//
// This client implements the AudioProcessingService interface by communicating
// with the Python gRPC service. It provides proper streaming support and
// follows the proto contracts exactly.
//
// Clean Architecture:
// - Implements domain AudioProcessingService interface
// - Handles gRPC communication with proper error handling
// - Maps between domain objects and proto messages
// - Provides streaming audio processing capabilities
// ============================================================================

package com.unhinged.infrastructure.audio

import com.unhinged.domain.audio.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.collect
import kotlinx.coroutines.flow.map
import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import io.grpc.StatusException
import java.io.ByteArrayOutputStream
import java.time.Instant

// Generated proto imports
import unhinged.audio.AudioServiceGrpcKt
import unhinged.audio.TTSRequest
import unhinged.audio.STTResponse
import unhinged.audio.ListVoicesRequest
import unhinged.audio.ProcessAudioRequest
import unhinged.audio.AudioFormat as ProtoAudioFormat
import unhinged.audio.AudioQuality as ProtoAudioQuality
import unhinged.common.StreamChunk
import unhinged.common.ChunkType
import unhinged.common.ChunkStatus

// ============================================================================
// Whisper TTS gRPC Client Implementation
// ============================================================================

/**
 * gRPC client implementation for Whisper TTS service
 * 
 * Communicates with the Python gRPC service to provide actual audio processing.
 * Maps domain objects to/from proto messages and handles streaming operations.
 */
class WhisperTtsGrpcClient(
    private val configuration: AudioConfiguration
) : AudioProcessingService {
    
    private val channel: ManagedChannel = ManagedChannelBuilder
        .forAddress(extractHost(configuration.whisperTtsHost), extractPort(configuration.whisperTtsHost))
        .usePlaintext()
        .build()
    
    private val stub = AudioServiceGrpcKt.AudioServiceCoroutineStub(channel)
    
    override suspend fun synthesizeText(synthesis: AudioSynthesis): Flow<AudioChunk> = flow {
        try {
            // Create proto request
            val request = TTSRequest.newBuilder()
                .setText(synthesis.text)
                .setVoiceId(synthesis.voiceId)
                .setOutputFormat(synthesis.outputFormat.toProto())
                .setSampleRate(synthesis.sampleRate)
                .setChannels(synthesis.channels)
                .setEnableSsml(synthesis.enableSsml)
                .build()
            
            // Call gRPC service and collect streaming response
            stub.textToSpeech(request).collect { streamChunk ->
                // Convert proto StreamChunk to domain AudioChunk
                val audioChunk = AudioChunk(
                    data = streamChunk.data.toByteArray(),
                    sequenceNumber = streamChunk.sequenceNumber,
                    isLast = streamChunk.isFinal,
                    metadata = streamChunk.structuredMap.mapValues { it.value.toString() }
                )
                emit(audioChunk)
            }
            
        } catch (e: StatusException) {
            throw AudioProcessingException("gRPC TTS failed: ${e.status.description}", e)
        } catch (e: Exception) {
            throw AudioProcessingException("Failed to synthesize speech: ${e.message}", e)
        }
    }
    
    override suspend fun transcribeAudio(
        audioChunks: Flow<AudioChunk>,
        options: AudioOptions
    ): AudioTranscription {
        try {
            // Convert domain AudioChunk flow to proto StreamChunk flow
            val protoChunks = audioChunks.map { chunk ->
                StreamChunk.newBuilder()
                    .setStreamId("stt_${System.currentTimeMillis()}")
                    .setSequenceNumber(chunk.sequenceNumber)
                    .setType(ChunkType.CHUNK_TYPE_DATA)
                    .setData(com.google.protobuf.ByteString.copyFrom(chunk.data))
                    .setIsFinal(chunk.isLast)
                    .setStatus(ChunkStatus.CHUNK_STATUS_PROCESSING)
                    .build()
            }
            
            // Call gRPC service
            val response = stub.speechToText(protoChunks)
            
            // Convert proto response to domain object
            return AudioTranscription(
                transcript = response.transcript,
                confidence = response.confidence,
                segments = response.segmentsList.map { segment ->
                    TranscriptSegment(
                        text = segment.text,
                        startTime = segment.startTime,
                        endTime = segment.endTime,
                        confidence = segment.confidence,
                        words = segment.wordsList.map { word ->
                            WordTiming(
                                word = word.word,
                                startTime = word.startTime,
                                endTime = word.endTime,
                                confidence = word.confidence
                            )
                        }
                    )
                },
                usage = AudioUsage(
                    durationSeconds = response.usage.duration.seconds.toFloat(),
                    bytesProcessed = response.usage.bytesProcessed,
                    sampleRate = response.usage.sampleRate,
                    channels = response.usage.channels,
                    format = response.usage.format
                ),
                metadata = STTMetadata(
                    model = response.metadata.model,
                    language = response.metadata.language,
                    processingTimeMs = response.metadata.processingTimeMs,
                    signalToNoiseRatio = response.metadata.signalToNoiseRatio,
                    speechRateWpm = response.metadata.speechRateWpm,
                    detectedLanguages = response.metadata.detectedLanguagesList,
                    hasBackgroundNoise = response.metadata.hasBackgroundNoise,
                    hasMultipleSpeakers = response.metadata.hasMultipleSpeakers,
                    detectedQuality = response.metadata.detectedQuality.toDomain()
                )
            )
            
        } catch (e: StatusException) {
            throw AudioProcessingException("gRPC STT failed: ${e.status.description}", e)
        } catch (e: Exception) {
            throw AudioProcessingException("Failed to transcribe audio: ${e.message}", e)
        }
    }
    
    override suspend fun processAudioFile(
        audioData: ByteArray,
        processingType: AudioProcessingType,
        options: AudioOptions
    ): AudioProcessingResult {
        try {
            val request = ProcessAudioRequest.newBuilder()
                .setProcessingType(processingType.toProto())
                .setAudioFile(
                    com.google.protobuf.ByteString.copyFrom(audioData)
                )
                .build()
            
            val response = stub.processAudioFile(request)
            
            return when (processingType) {
                AudioProcessingType.TRANSCRIBE -> {
                    AudioProcessingResult.TranscriptionResult(
                        AudioTranscription(
                            transcript = response.transcript,
                            confidence = 0.9f, // Default confidence
                            segments = listOf(
                                TranscriptSegment(
                                    text = response.transcript,
                                    startTime = 0.0f,
                                    endTime = calculateDuration(audioData),
                                    confidence = 0.9f
                                )
                            ),
                            usage = AudioUsage(
                                durationSeconds = calculateDuration(audioData),
                                bytesProcessed = audioData.size.toLong(),
                                sampleRate = 16000,
                                channels = 1,
                                format = "wav"
                            ),
                            metadata = STTMetadata(
                                model = "whisper-base",
                                language = "en",
                                processingTimeMs = 0.0f,
                                signalToNoiseRatio = 0.0f,
                                speechRateWpm = 0.0f,
                                detectedLanguages = listOf("en"),
                                hasBackgroundNoise = false,
                                hasMultipleSpeakers = false,
                                detectedQuality = AudioQuality.STANDARD
                            )
                        )
                    )
                }
                else -> throw NotImplementedError("Processing type $processingType not implemented")
            }
            
        } catch (e: StatusException) {
            throw AudioProcessingException("gRPC audio processing failed: ${e.status.description}", e)
        } catch (e: Exception) {
            throw AudioProcessingException("Failed to process audio file: ${e.message}", e)
        }
    }
    
    override suspend fun convertAudioFormat(
        audioData: ByteArray,
        sourceFormat: AudioFormat,
        targetFormat: AudioFormat,
        options: AudioOptions
    ): ByteArray {
        throw NotImplementedError("Audio format conversion not yet implemented")
    }
    
    override suspend fun analyzeAudio(
        audioData: ByteArray,
        analysisTypes: List<AudioAnalysisType>
    ): AudioAnalysisResult {
        throw NotImplementedError("Audio analysis not yet implemented")
    }
    
    override suspend fun healthCheck(): AudioServiceHealth {
        try {
            val request = unhinged.common.HealthCheckRequest.newBuilder().build()
            val response = stub.healthCheck(request)
            
            return AudioServiceHealth(
                isHealthy = response.status == "healthy",
                whisperModelLoaded = response.detailsMap["whisper_model_loaded"]?.toBoolean() ?: false,
                cudaAvailable = response.detailsMap["cuda_available"]?.toBoolean() ?: false,
                version = response.detailsMap["version"] ?: "unknown",
                capabilities = listOf("tts", "stt", "voice_management")
            )
            
        } catch (e: StatusException) {
            return AudioServiceHealth(
                isHealthy = false,
                whisperModelLoaded = false,
                cudaAvailable = false,
                version = "unknown",
                capabilities = emptyList()
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
    
    /**
     * Cleanup resources
     */
    fun shutdown() {
        channel.shutdown()
    }
    
    // ============================================================================
    // Helper Functions
    // ============================================================================
    
    private fun extractHost(hostPort: String): String {
        return hostPort.substringAfter("://").substringBefore(":")
    }
    
    private fun extractPort(hostPort: String): Int {
        return hostPort.substringAfterLast(":").toIntOrNull() ?: 9091
    }
    
    private fun calculateDuration(audioBytes: ByteArray): Float {
        // Rough estimate: assume 16kHz, 16-bit, mono
        val bytesPerSecond = 16000 * 2 * 1
        return audioBytes.size.toFloat() / bytesPerSecond
    }
}

// ============================================================================
// Extension Functions for Proto Mapping
// ============================================================================

/**
 * Converts domain AudioFormat to proto AudioFormat
 */
private fun AudioFormat.toProto(): ProtoAudioFormat {
    return when (this) {
        AudioFormat.WAV -> ProtoAudioFormat.AUDIO_FORMAT_WAV
        AudioFormat.MP3 -> ProtoAudioFormat.AUDIO_FORMAT_MP3
        AudioFormat.OGG -> ProtoAudioFormat.AUDIO_FORMAT_OGG
        AudioFormat.FLAC -> ProtoAudioFormat.AUDIO_FORMAT_FLAC
        AudioFormat.PCM -> ProtoAudioFormat.AUDIO_FORMAT_PCM
        AudioFormat.OPUS -> ProtoAudioFormat.AUDIO_FORMAT_OPUS
        AudioFormat.AAC -> ProtoAudioFormat.AUDIO_FORMAT_AAC
        else -> ProtoAudioFormat.AUDIO_FORMAT_UNSPECIFIED
    }
}

/**
 * Converts proto AudioQuality to domain AudioQuality
 */
private fun ProtoAudioQuality.toDomain(): AudioQuality {
    return when (this) {
        ProtoAudioQuality.AUDIO_QUALITY_LOW -> AudioQuality.LOW
        ProtoAudioQuality.AUDIO_QUALITY_STANDARD -> AudioQuality.STANDARD
        ProtoAudioQuality.AUDIO_QUALITY_HIGH -> AudioQuality.HIGH
        ProtoAudioQuality.AUDIO_QUALITY_PREMIUM -> AudioQuality.PREMIUM
        else -> AudioQuality.STANDARD
    }
}

/**
 * Converts domain AudioProcessingType to proto ProcessingType
 */
private fun AudioProcessingType.toProto(): unhinged.audio.ProcessingType {
    return when (this) {
        AudioProcessingType.TRANSCRIBE -> unhinged.audio.ProcessingType.PROCESSING_TYPE_TRANSCRIBE
        AudioProcessingType.TRANSLATE -> unhinged.audio.ProcessingType.PROCESSING_TYPE_TRANSLATE
        AudioProcessingType.ENHANCE -> unhinged.audio.ProcessingType.PROCESSING_TYPE_ENHANCE
        AudioProcessingType.CONVERT -> unhinged.audio.ProcessingType.PROCESSING_TYPE_CONVERT
    }
}
