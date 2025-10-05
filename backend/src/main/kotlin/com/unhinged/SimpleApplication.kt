// ============================================================================
// Unhinged Backend - Clean Architecture Implementation
// ============================================================================
//
// @file SimpleApplication.kt
// @version 2.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Clean architecture backend with domain-driven design
// ============================================================================

package com.unhinged

import com.unhinged.application.chat.ChatUseCases
import com.unhinged.infrastructure.chat.InMemoryChatMessageRepository
import com.unhinged.infrastructure.chat.InMemoryChatSessionRepository
import com.unhinged.presentation.http.ChatController
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import org.slf4j.LoggerFactory

/**
 * Main application entry point - Clean Architecture
 */
fun main() {
    val logger = LoggerFactory.getLogger("UnhingedApplication")

    logger.info("🚀 Starting Unhinged Backend v2.0.0 - Clean Architecture")

    // Initialize repositories (in-memory for now)
    val messageRepository = InMemoryChatMessageRepository()
    val sessionRepository = InMemoryChatSessionRepository()

    // Initialize use cases
    val chatUseCases = ChatUseCases(messageRepository, sessionRepository)

    // Initialize controllers
    val chatController = ChatController(chatUseCases)

    logger.info("✅ Dependencies initialized")

    embeddedServer(Netty, port = 8080, host = "0.0.0.0") {
        // Configure JSON serialization
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }

        // Configure CORS for frontend
        install(CORS) {
            allowMethod(HttpMethod.Options)
            allowMethod(HttpMethod.Post)
            allowMethod(HttpMethod.Get)
            allowMethod(HttpMethod.Put)
            allowMethod(HttpMethod.Delete)
            allowHeader(HttpHeaders.AccessControlAllowOrigin)
            allowHeader(HttpHeaders.ContentType)
            allowHeader(HttpHeaders.Authorization)
            anyHost() // For development only
        }

        // Configure routing with clean architecture
        routing {
            // Legacy endpoint for backward compatibility with existing frontend
            post("/chat") {
                try {
                    val body = call.receiveText()
                    logger.info("Legacy chat request: $body")

                    // Parse simple JSON or use as plain text
                    val prompt = try {
                        val json = Json.parseToJsonElement(body).jsonObject
                        json["prompt"]?.toString()?.removeSurrounding("\"") ?: body
                    } catch (e: Exception) {
                        body
                    }

                    // Create session and send message
                    val session = chatUseCases.createSession(
                        com.unhinged.application.chat.CreateSessionRequest(
                            userId = "legacy-user",
                            title = "Legacy Chat"
                        )
                    )

                    val result = chatUseCases.sendMessage(
                        com.unhinged.application.chat.SendMessageRequest(
                            content = prompt,
                            sessionId = session.id,
                            userId = "legacy-user"
                        )
                    )

                    // Return just the response text for legacy compatibility
                    call.respondText(result.assistantMessage.content)

                } catch (e: Exception) {
                    logger.error("Error in legacy chat endpoint: ${e.message}", e)
                    call.respondText("Error processing request: ${e.message}")
                }
            }

            // Configure clean architecture routes
            chatController.configureRoutes(this)

            // Root endpoint
            get("/") {
                call.respondText(
                    "🔥 Unhinged Backend v2.0.0 - Clean Architecture\n\n" +
                    "📋 Available endpoints:\n" +
                    "- GET    /                           - This info\n" +
                    "- GET    /api/v1/health             - Health check\n" +
                    "- POST   /chat                      - Legacy chat (backward compatible)\n" +
                    "- POST   /api/v1/chat               - Modern chat API\n" +
                    "- POST   /api/v1/sessions           - Create session\n" +
                    "- GET    /api/v1/sessions/user/{id} - Get user sessions\n" +
                    "- GET    /api/v1/sessions/{id}      - Get session\n" +
                    "- GET    /api/v1/sessions/{id}/messages - Get conversation\n" +
                    "- DELETE /api/v1/sessions/{id}      - Delete session\n\n" +
                    "🏗️  Architecture: Domain-Driven Design with Clean Architecture\n" +
                    "📦 Layers: Domain → Application → Infrastructure → Presentation\n" +
                    "🔄 Status: Ready for production scaling\n"
                )
            }
        }

    }.start(wait = true)
}


