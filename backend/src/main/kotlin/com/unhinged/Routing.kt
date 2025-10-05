package com.unhinged

import com.unhinged.service.LlmService
import com.unhinged.service.TtsService
import com.unhinged.service.ToolsService
import com.unhinged.service.ToolDefinition
import com.unhinged.service.ToolExecutionRequest
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

        // E-Tools endpoints
        get("/tools/list") {
            try {
                val category = call.request.queryParameters["category"]
                val response = if (category != null) {
                    mapOf("tools" to ToolsService.getToolsByCategory(category))
                } else {
                    ToolsService.getAllTools()
                }
                call.respond(HttpStatusCode.OK, response)
            } catch (e: Exception) {
                println("Tools list request failed: ${e.message}")
                call.respond(
                    HttpStatusCode.InternalServerError,
                    mapOf("error" to (e.message ?: "Failed to list tools"))
                )
            }
        }

        get("/tools/{id}") {
            try {
                val toolId = call.parameters["id"] ?: throw IllegalArgumentException("Tool ID required")
                val tool = ToolsService.getTool(toolId)
                if (tool != null) {
                    call.respond(HttpStatusCode.OK, tool)
                } else {
                    call.respond(HttpStatusCode.NotFound, mapOf("error" to "Tool not found"))
                }
            } catch (e: Exception) {
                println("Tool info request failed: ${e.message}")
                call.respond(
                    HttpStatusCode.InternalServerError,
                    mapOf("error" to (e.message ?: "Failed to get tool info"))
                )
            }
        }

        post("/tools/register") {
            try {
                val toolDefinition = call.receive<ToolDefinition>()
                val success = ToolsService.registerTool(toolDefinition)
                if (success) {
                    call.respond(HttpStatusCode.Created, mapOf("message" to "Tool registered successfully", "id" to toolDefinition.id))
                } else {
                    call.respond(HttpStatusCode.BadRequest, mapOf("error" to "Failed to register tool"))
                }
            } catch (e: Exception) {
                println("Tool registration failed: ${e.message}")
                call.respond(
                    HttpStatusCode.BadRequest,
                    mapOf("error" to (e.message ?: "Tool registration failed"))
                )
            }
        }

        post("/tools/execute") {
            try {
                val executionRequest = call.receive<ToolExecutionRequest>()
                val result = ToolsService.executeTool(executionRequest)
                call.respond(HttpStatusCode.OK, result)
            } catch (e: Exception) {
                println("Tool execution failed: ${e.message}")
                call.respond(
                    HttpStatusCode.InternalServerError,
                    mapOf("error" to (e.message ?: "Tool execution failed"))
                )
            }
        }

        get("/tools/search") {
            try {
                val query = call.request.queryParameters["q"] ?: throw IllegalArgumentException("Search query required")
                val results = ToolsService.searchTools(query)
                call.respond(HttpStatusCode.OK, mapOf("tools" to results, "count" to results.size))
            } catch (e: Exception) {
                println("Tool search failed: ${e.message}")
                call.respond(
                    HttpStatusCode.InternalServerError,
                    mapOf("error" to (e.message ?: "Tool search failed"))
                )
            }
        }

        get("/tools/history") {
            try {
                val limit = call.request.queryParameters["limit"]?.toIntOrNull() ?: 100
                val history = ToolsService.getExecutionHistory(limit)
                call.respond(HttpStatusCode.OK, mapOf("history" to history, "count" to history.size))
            } catch (e: Exception) {
                println("Tool history request failed: ${e.message}")
                call.respond(
                    HttpStatusCode.InternalServerError,
                    mapOf("error" to (e.message ?: "Failed to get tool history"))
                )
            }
        }

        // Health check endpoint
        get("/health") {
            call.respond(HttpStatusCode.OK, mapOf(
                "status" to "healthy",
                "timestamp" to System.currentTimeMillis(),
                "services" to mapOf(
                    "llm" to "available",
                    "tts" to "available",
                    "tools" to "available"
                )
            ))
        }

        // Platform info endpoint
        get("/info") {
            call.respond(HttpStatusCode.OK, mapOf(
                "platform" to "Unhinged",
                "version" to "1.0.0-unhinged",
                "features" to listOf("llm", "tts", "tools", "e-cli-integration"),
                "endpoints" to mapOf(
                    "chat" to "/chat",
                    "tts" to "/tts/*",
                    "tools" to "/tools/*"
                )
            ))
        }
    }
}

@Serializable
data class TtsSynthesizeRequest(
    val text: String,
    val language: String? = "en"
)

