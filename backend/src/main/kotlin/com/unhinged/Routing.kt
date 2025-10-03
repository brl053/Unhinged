package com.unhinged

import com.unhinged.service.LlmService
import com.unhinged.service.TtsService
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.Serializable

fun Application.configureRouting() {
    install(CORS) {
        anyHost() // Allows all origins (you can specify specific origins later)
        allowCredentials = true
        allowNonSimpleContentTypes = true
        maxAgeInSeconds = 3600
        allowHeader(HttpHeaders.ContentType) // Allow 'Content-Type' header
        allowMethod(HttpMethod.Post) // Allow 'POST' method
        allowMethod(HttpMethod.Options) // Allow 'OPTIONS' method for preflight
    }

    routing {
        get("/") {
            call.respondText("Hello World!")
        }
        post("/chat") {
            // TODO: Prompt is actually JSON. We need to improve FE/BE connection. Good for PoC.
            val prompt = call.receiveText()
            println("Received prompt: $prompt")
            val response = LlmService.queryLlmStream(prompt)
            call.respondText(response)
        }

        // TTS endpoints
        post("/tts/synthesize") {
            try {
                val request = call.receive<TtsSynthesizeRequest>()
                println("TTS request: ${request.text} (${request.language})")

                val audioBytes = TtsService.synthesizeText(request.text, request.language ?: "en")

                call.respondBytes(
                    bytes = audioBytes,
                    contentType = ContentType.Audio.MPEG,
                    status = HttpStatusCode.OK
                )
            } catch (e: Exception) {
                println("TTS synthesis failed: ${e.message}")
                call.respond(
                    HttpStatusCode.InternalServerError,
                    mapOf("error" to (e.message ?: "Speech synthesis failed"))
                )
            }
        }

        get("/tts/health") {
            try {
                val health = TtsService.checkHealth()
                call.respond(HttpStatusCode.OK, health)
            } catch (e: Exception) {
                println("TTS health check failed: ${e.message}")
                call.respond(
                    HttpStatusCode.ServiceUnavailable,
                    mapOf("error" to (e.message ?: "TTS service unavailable"))
                )
            }
        }

        get("/tts/info") {
            try {
                val info = TtsService.getServiceInfo()
                call.respond(HttpStatusCode.OK, info)
            } catch (e: Exception) {
                println("TTS info request failed: ${e.message}")
                call.respond(
                    HttpStatusCode.InternalServerError,
                    mapOf("error" to (e.message ?: "Failed to get TTS info"))
                )
            }
        }
    }
}

@Serializable
data class TtsSynthesizeRequest(
    val text: String,
    val language: String? = "en"
)

