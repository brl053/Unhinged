// ============================================================================
// Audio HTTP Controller - Presentation Layer
// ============================================================================
//
// @file AudioController.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description HTTP REST endpoints for audio processing operations
//
// This controller provides HTTP REST endpoints as a bridge to the audio
// functionality while we implement the full gRPC service. It follows
// clean architecture by delegating to use cases.
//
// Proto Alignment:
// - Endpoints map to proto service methods
// - Request/response DTOs align with proto messages
// - Will be replaced by gRPC service implementation
// ============================================================================

package com.unhinged.presentation.http

import com.unhinged.application.audio.*
import com.unhinged.domain.audio.*
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.toList
import kotlinx.serialization.*

// ============================================================================
// Audio Controller
// ============================================================================

/**
 * HTTP controller for audio operations
 * 
 * Provides REST endpoints that map to the proto service methods.
 * This is a temporary bridge until full gRPC implementation.
 */
class AudioController(
    private val textToSpeechUseCase: TextToSpeechUseCase,
    private val speechToTextUseCase: SpeechToTextUseCase,
    private val voiceManagementUseCase: VoiceManagementUseCase,
    private val processAudioFileUseCase: ProcessAudioFileUseCase
) {
    
    fun configureRoutes(routing: Routing) {
        routing.route("/api/v1/audio") {
            
            // Text-to-Speech endpoint
            post("/synthesize") {
                try {
                    val request = call.receive<TtsSynthesizeRequest>()
                    val userId = call.request.headers["X-User-ID"] ?: "anonymous"
                    
                    // Convert HTTP request to proto-style request
                    val ttsRequest = unhinged.audio.TTSRequest.newBuilder()
                        .setText(request.text)
                        .setVoiceId(request.voiceId ?: "voice-en-us-female-1")
                        .setOutputFormat(unhinged.audio.AudioFormat.AUDIO_FORMAT_MP3)
                        .setSampleRate(request.sampleRate ?: 22050)
                        .setChannels(request.channels ?: 1)
                        .setEnableSsml(request.enableSsml ?: false)
                        .build()
                    
                    // Execute use case
                    val audioChunks = textToSpeechUseCase.execute(ttsRequest, userId).toList()
                    
                    // Combine chunks into single audio file
                    val audioData = audioChunks.flatMap { it.data.toList() }.toByteArray()
                    
                    call.respondBytes(
                        bytes = audioData,
                        contentType = ContentType.Audio.MPEG,
                        status = HttpStatusCode.OK
                    )
                    
                } catch (e: AudioValidationException) {
                    call.respond(
                        HttpStatusCode.BadRequest,
                        ErrorResponse("Validation failed", e.errors.map { it.message })
                    )
                } catch (e: AudioNotFoundException) {
                    call.respond(
                        HttpStatusCode.NotFound,
                        ErrorResponse("Resource not found", listOf(e.message ?: "Unknown error"))
                    )
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.InternalServerError,
                        ErrorResponse("Speech synthesis failed", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
            
            // Speech-to-Text endpoint
            post("/transcribe") {
                try {
                    val userId = call.request.headers["X-User-ID"] ?: "anonymous"
                    
                    // Get audio data from multipart request
                    val multipart = call.receiveMultipart()
                    var audioData: ByteArray? = null
                    
                    multipart.forEachPart { part ->
                        when (part) {
                            is PartData.FileItem -> {
                                if (part.name == "audio") {
                                    audioData = part.streamProvider().readBytes()
                                }
                            }
                            else -> {}
                        }
                        part.dispose()
                    }
                    
                    if (audioData == null) {
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse("No audio file provided", emptyList())
                        )
                        return@post
                    }
                    
                    // Convert to audio chunks flow
                    val audioChunks = flow {
                        emit(AudioChunk(audioData!!, 1, true))
                    }
                    
                    // Execute use case
                    val transcription = speechToTextUseCase.execute(audioChunks, userId)
                    
                    call.respond(
                        HttpStatusCode.OK,
                        SttTranscribeResponse(
                            text = transcription.transcript,
                            confidence = transcription.confidence,
                            language = transcription.metadata.language,
                            segments = transcription.segments.map { segment ->
                                TranscriptSegmentDto(
                                    text = segment.text,
                                    startTime = segment.startTime,
                                    endTime = segment.endTime,
                                    confidence = segment.confidence
                                )
                            }
                        )
                    )
                    
                } catch (e: AudioValidationException) {
                    call.respond(
                        HttpStatusCode.BadRequest,
                        ErrorResponse("Validation failed", e.errors.map { it.message })
                    )
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.InternalServerError,
                        ErrorResponse("Speech transcription failed", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
            
            // List voices endpoint
            get("/voices") {
                try {
                    val language = call.request.queryParameters["language"]
                    val gender = call.request.queryParameters["gender"]?.let { 
                        VoiceGender.valueOf(it.uppercase()) 
                    }
                    val style = call.request.queryParameters["style"]?.let { 
                        VoiceStyle.valueOf(it.uppercase()) 
                    }
                    val premiumOnly = call.request.queryParameters["premium_only"]?.toBoolean() ?: false
                    val limit = call.request.queryParameters["limit"]?.toInt() ?: 50
                    val offset = call.request.queryParameters["offset"]?.toInt() ?: 0
                    
                    val voices = voiceManagementUseCase.listVoices(
                        language, gender, style, premiumOnly, limit, offset
                    )
                    
                    call.respond(
                        HttpStatusCode.OK,
                        ListVoicesResponse(
                            voices = voices.map { it.toDto() },
                            total = voices.size,
                            hasMore = voices.size == limit
                        )
                    )
                    
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.InternalServerError,
                        ErrorResponse("Failed to list voices", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
            
            // Get voice endpoint
            get("/voices/{id}") {
                try {
                    val voiceId = call.parameters["id"] ?: throw IllegalArgumentException("Voice ID required")
                    val voice = voiceManagementUseCase.getVoice(voiceId)
                    
                    call.respond(HttpStatusCode.OK, voice.toDto())
                    
                } catch (e: AudioNotFoundException) {
                    call.respond(
                        HttpStatusCode.NotFound,
                        ErrorResponse("Voice not found", listOf(e.message ?: "Unknown error"))
                    )
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.InternalServerError,
                        ErrorResponse("Failed to get voice", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
            
            // Search voices endpoint
            get("/voices/search") {
                try {
                    val query = call.request.queryParameters["q"] 
                        ?: throw IllegalArgumentException("Search query required")
                    val limit = call.request.queryParameters["limit"]?.toInt() ?: 20
                    
                    val voices = voiceManagementUseCase.searchVoices(query, limit)
                    
                    call.respond(
                        HttpStatusCode.OK,
                        SearchVoicesResponse(
                            voices = voices.map { it.toDto() },
                            query = query,
                            count = voices.size
                        )
                    )
                    
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.InternalServerError,
                        ErrorResponse("Voice search failed", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
            
            // Health check endpoint
            get("/health") {
                try {
                    // This would check the health of the audio processing service
                    call.respond(
                        HttpStatusCode.OK,
                        mapOf(
                            "status" to "healthy",
                            "timestamp" to System.currentTimeMillis(),
                            "service" to "audio-processing",
                            "version" to "1.0.0"
                        )
                    )
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.ServiceUnavailable,
                        ErrorResponse("Audio service unhealthy", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
        }
    }
}

// ============================================================================
// HTTP DTOs (Proto-Aligned)
// ============================================================================

@Serializable
data class TtsSynthesizeRequest(
    val text: String,
    val voiceId: String? = null,
    val language: String? = "en",
    val sampleRate: Int? = null,
    val channels: Int? = null,
    val enableSsml: Boolean? = null
)

@Serializable
data class SttTranscribeResponse(
    val text: String,
    val confidence: Float,
    val language: String,
    val segments: List<TranscriptSegmentDto>
)

@Serializable
data class TranscriptSegmentDto(
    val text: String,
    val startTime: Float,
    val endTime: Float,
    val confidence: Float
)

@Serializable
data class VoiceDto(
    val id: String,
    val name: String,
    val displayName: String,
    val description: String,
    val language: String,
    val languageCode: String,
    val gender: String,
    val age: String,
    val style: String,
    val supportedFormats: List<String>,
    val supportedSampleRates: List<Int>,
    val isAvailable: Boolean,
    val isPremium: Boolean,
    val costPerCharacter: Float,
    val previewUrl: String? = null,
    val previewText: String? = null
)

@Serializable
data class ListVoicesResponse(
    val voices: List<VoiceDto>,
    val total: Int,
    val hasMore: Boolean
)

@Serializable
data class SearchVoicesResponse(
    val voices: List<VoiceDto>,
    val query: String,
    val count: Int
)

@Serializable
data class ErrorResponse(
    val error: String,
    val details: List<String>
)

// ============================================================================
// Extension Functions
// ============================================================================

/**
 * Converts domain Voice to DTO
 */
private fun Voice.toDto(): VoiceDto {
    return VoiceDto(
        id = this.id,
        name = this.name,
        displayName = this.displayName,
        description = this.description,
        language = this.language,
        languageCode = this.languageCode,
        gender = this.gender.name,
        age = this.age.name,
        style = this.style.name,
        supportedFormats = this.supportedFormats.map { it.name },
        supportedSampleRates = this.supportedSampleRates,
        isAvailable = this.isAvailable,
        isPremium = this.isPremium,
        costPerCharacter = this.costPerCharacter,
        previewUrl = this.previewUrl,
        previewText = this.previewText
    )
}
