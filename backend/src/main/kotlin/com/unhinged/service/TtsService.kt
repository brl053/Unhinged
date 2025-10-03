package com.unhinged.service

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.*

/**
 * Text-to-Speech Service
 * 
 * Provides integration with the Whisper TTS service for speech synthesis.
 * Handles communication with the Python Flask service running on port 8000.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

@Serializable
data class TtsRequest(
    val text: String,
    val language: String = "en"
)

@Serializable
data class TtsHealthResponse(
    val status: String,
    val whisper_model_loaded: Boolean,
    val cuda_available: Boolean,
    val service: String,
    val version: String,
    val capabilities: List<String>
)

@Serializable
data class TtsErrorResponse(
    val error: String
)

object TtsService {
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) { json() }
    }

    /**
     * Synthesizes text to speech using the Whisper TTS service
     * 
     * @param text The text to convert to speech
     * @param language The language code (default: "en")
     * @return ByteArray containing the MP3 audio data
     * @throws Exception if synthesis fails
     */
    suspend fun synthesizeText(text: String, language: String = "en"): ByteArray {
        try {
            val whisperTtsHost = System.getenv("WHISPER_TTS_HOST") ?: "http://localhost:8000"
            
            val requestBody = TtsRequest(
                text = text,
                language = language
            )

            val response: HttpResponse = client.post("$whisperTtsHost/synthesize") {
                contentType(ContentType.Application.Json)
                setBody(requestBody)
            }

            if (!response.status.isSuccess()) {
                val errorBody = response.bodyAsText()
                throw Exception("TTS service error: ${response.status.value} - $errorBody")
            }

            // Return the audio bytes
            return response.body<ByteArray>()

        } catch (e: Exception) {
            throw Exception("Failed to synthesize speech: ${e.message}", e)
        }
    }

    /**
     * Checks the health of the TTS service
     * 
     * @return TtsHealthResponse containing service status
     * @throws Exception if health check fails
     */
    suspend fun checkHealth(): TtsHealthResponse {
        try {
            val whisperTtsHost = System.getenv("WHISPER_TTS_HOST") ?: "http://localhost:8000"
            
            val response: HttpResponse = client.get("$whisperTtsHost/health")

            if (!response.status.isSuccess()) {
                throw Exception("TTS health check failed: ${response.status.value}")
            }

            return response.body<TtsHealthResponse>()

        } catch (e: Exception) {
            throw Exception("Failed to check TTS service health: ${e.message}", e)
        }
    }

    /**
     * Gets information about the TTS service capabilities
     * 
     * @return Map containing service information
     * @throws Exception if info request fails
     */
    suspend fun getServiceInfo(): Map<String, Any> {
        try {
            val whisperTtsHost = System.getenv("WHISPER_TTS_HOST") ?: "http://localhost:8000"
            
            val response: HttpResponse = client.get("$whisperTtsHost/info")

            if (!response.status.isSuccess()) {
                throw Exception("TTS info request failed: ${response.status.value}")
            }

            return response.body<Map<String, Any>>()

        } catch (e: Exception) {
            throw Exception("Failed to get TTS service info: ${e.message}", e)
        }
    }
}
