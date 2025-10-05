package com.unhinged

import com.unhinged.service.LlmService
import com.unhinged.events.Events
import com.unhinged.events.LLMInferenceEvent
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.util.*

@Serializable
data class LLMRequest(
    val prompt: String,
    val model: String = "llama3.2",
    val userId: String,
    val sessionId: String
)

@Serializable
data class LLMResponse(
    val response: String,
    val eventId: String,
    val traceId: String,
    val success: Boolean,
    val latencyMs: Long
)

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

        post("/api/llm/infer") {
            val startTime = System.currentTimeMillis()
            val traceId = UUID.randomUUID().toString()

            try {
                val request = call.receive<LLMRequest>()

                // Call LLM service
                val response = LlmService.queryLlmStream(request.prompt)
                val endTime = System.currentTimeMillis()
                val latencyMs = endTime - startTime

                // Emit event
                val eventId = Events.emit().emitLLMInference(
                    traceId = traceId,
                    userId = request.userId,
                    sessionId = request.sessionId,
                    event = LLMInferenceEvent(
                        prompt = request.prompt,
                        response = response,
                        model = request.model,
                        prompt_tokens = request.prompt.split(" ").size, // Simple approximation
                        response_tokens = response.split(" ").size,
                        latency_ms = latencyMs,
                        success = true
                    )
                )

                call.respond(LLMResponse(
                    response = response,
                    eventId = eventId,
                    traceId = traceId,
                    success = true,
                    latencyMs = latencyMs
                ))

            } catch (e: Exception) {
                val endTime = System.currentTimeMillis()
                val latencyMs = endTime - startTime

                // Emit error event
                Events.emit().emitEvent(
                    eventType = "llm.inference.error",
                    traceId = traceId,
                    userId = "unknown",
                    sessionId = "unknown",
                    payload = mapOf(
                        "error" to e.message.orEmpty(),
                        "latency_ms" to latencyMs.toString()
                    )
                )

                call.respond(HttpStatusCode.InternalServerError, mapOf("error" to e.message))
            }
        }

        // Session events API for LLM context
        get("/api/sessions/{sessionId}/events") {
            val sessionId = call.parameters["sessionId"] ?: return@get call.respond(HttpStatusCode.BadRequest)
            val limit = call.request.queryParameters["limit"]?.toIntOrNull() ?: 100

            val events = Events.emit().getSessionEvents(sessionId, limit)
            call.respond(events)
        }
    }
}

