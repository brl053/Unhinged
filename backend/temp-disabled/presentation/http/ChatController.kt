// ============================================================================
// Chat HTTP Controller - Presentation Layer
// ============================================================================
//
// @file ChatController.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description HTTP endpoints for chat functionality
// ============================================================================

package com.unhinged.presentation.http

import com.unhinged.application.chat.*
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.Serializable
import org.slf4j.LoggerFactory

/**
 * HTTP DTOs for the chat API
 */
@Serializable
data class ChatRequest(
    val prompt: String,
    val sessionId: String? = null,
    val userId: String = "default-user"
)

@Serializable
data class ChatResponse(
    val response: String,
    val sessionId: String,
    val messageId: String,
    val processingTimeMs: Long
)

@Serializable
data class SessionResponse(
    val sessionId: String,
    val userId: String,
    val title: String?,
    val createdAt: String,
    val isActive: Boolean
)

@Serializable
data class ConversationResponse(
    val sessionId: String,
    val messages: List<MessageResponse>,
    val totalCount: Int
)

@Serializable
data class MessageResponse(
    val id: String,
    val content: String,
    val role: String,
    val timestamp: String
)

/**
 * Chat HTTP controller
 */
class ChatController(
    private val chatUseCases: ChatUseCases
) {
    private val logger = LoggerFactory.getLogger(ChatController::class.java)
    
    fun configureRoutes(routing: Routing) {
        routing.apply {
            route("/api/v1/chat") {
                
                // Main chat endpoint - compatible with existing frontend
                post {
                    try {
                        val request = call.receive<ChatRequest>()
                        logger.info("Received chat request: ${request.prompt}")
                        
                        // Create session if not provided
                        val sessionId = request.sessionId ?: run {
                            val newSession = chatUseCases.createSession(
                                CreateSessionRequest(
                                    userId = request.userId,
                                    title = "Chat Session"
                                )
                            )
                            newSession.id
                        }
                        
                        // Send message and get response
                        val result = chatUseCases.sendMessage(
                            SendMessageRequest(
                                content = request.prompt,
                                sessionId = sessionId,
                                userId = request.userId
                            )
                        )
                        
                        val response = ChatResponse(
                            response = result.assistantMessage.content,
                            sessionId = sessionId,
                            messageId = result.assistantMessage.id,
                            processingTimeMs = result.processingTimeMs
                        )
                        
                        logger.info("Sending response: ${response.response}")
                        call.respond(HttpStatusCode.OK, response)
                        
                    } catch (e: Exception) {
                        logger.error("Error processing chat request: ${e.message}", e)
                        call.respond(
                            HttpStatusCode.InternalServerError,
                            mapOf("error" to "Failed to process chat request: ${e.message}")
                        )
                    }
                }
                
                // Legacy endpoint for backward compatibility
                post("/message") {
                    try {
                        val request = call.receive<ChatRequest>()
                        
                        val sessionId = request.sessionId ?: run {
                            val newSession = chatUseCases.createSession(
                                CreateSessionRequest(userId = request.userId)
                            )
                            newSession.id
                        }
                        
                        val result = chatUseCases.sendMessage(
                            SendMessageRequest(
                                content = request.prompt,
                                sessionId = sessionId,
                                userId = request.userId
                            )
                        )
                        
                        // Return just the response text for legacy compatibility
                        call.respondText(result.assistantMessage.content)
                        
                    } catch (e: Exception) {
                        logger.error("Error in legacy chat endpoint: ${e.message}", e)
                        call.respond(
                            HttpStatusCode.InternalServerError,
                            "Error processing request: ${e.message}"
                        )
                    }
                }
            }
            
            route("/api/v1/sessions") {
                
                // Create new session
                post {
                    try {
                        val request = call.receive<CreateSessionRequest>()
                        val session = chatUseCases.createSession(request)
                        
                        call.respond(HttpStatusCode.Created, SessionResponse(
                            sessionId = session.id,
                            userId = session.userId,
                            title = session.title,
                            createdAt = session.createdAt,
                            isActive = session.isActive
                        ))
                        
                    } catch (e: Exception) {
                        logger.error("Error creating session: ${e.message}", e)
                        call.respond(
                            HttpStatusCode.BadRequest,
                            mapOf("error" to e.message)
                        )
                    }
                }
                
                // Get user sessions
                get("/user/{userId}") {
                    try {
                        val userId = call.parameters["userId"] 
                            ?: return@get call.respond(HttpStatusCode.BadRequest, "Missing userId")
                        
                        val sessions = chatUseCases.getUserSessions(userId)
                        val response = sessions.map { session ->
                            SessionResponse(
                                sessionId = session.id,
                                userId = session.userId,
                                title = session.title,
                                createdAt = session.createdAt,
                                isActive = session.isActive
                            )
                        }
                        
                        call.respond(HttpStatusCode.OK, response)
                        
                    } catch (e: Exception) {
                        logger.error("Error getting user sessions: ${e.message}", e)
                        call.respond(
                            HttpStatusCode.InternalServerError,
                            mapOf("error" to e.message)
                        )
                    }
                }
                
                // Get specific session
                get("/{sessionId}") {
                    try {
                        val sessionId = call.parameters["sessionId"]
                            ?: return@get call.respond(HttpStatusCode.BadRequest, "Missing sessionId")
                        
                        val session = chatUseCases.getSession(sessionId)
                            ?: return@get call.respond(HttpStatusCode.NotFound, "Session not found")
                        
                        call.respond(HttpStatusCode.OK, SessionResponse(
                            sessionId = session.id,
                            userId = session.userId,
                            title = session.title,
                            createdAt = session.createdAt,
                            isActive = session.isActive
                        ))
                        
                    } catch (e: Exception) {
                        logger.error("Error getting session: ${e.message}", e)
                        call.respond(
                            HttpStatusCode.InternalServerError,
                            mapOf("error" to e.message)
                        )
                    }
                }
                
                // Get conversation history
                get("/{sessionId}/messages") {
                    try {
                        val sessionId = call.parameters["sessionId"]
                            ?: return@get call.respond(HttpStatusCode.BadRequest, "Missing sessionId")
                        
                        val limit = call.request.queryParameters["limit"]?.toIntOrNull() ?: 50
                        val since = call.request.queryParameters["since"]
                        
                        val conversation = chatUseCases.getConversation(
                            GetConversationRequest(
                                sessionId = sessionId,
                                limit = limit,
                                since = since
                            )
                        )
                        
                        val response = ConversationResponse(
                            sessionId = conversation.sessionId,
                            messages = conversation.messages.map { msg ->
                                MessageResponse(
                                    id = msg.id,
                                    content = msg.content,
                                    role = msg.role.name.lowercase(),
                                    timestamp = msg.timestamp
                                )
                            },
                            totalCount = conversation.totalCount
                        )
                        
                        call.respond(HttpStatusCode.OK, response)
                        
                    } catch (e: Exception) {
                        logger.error("Error getting conversation: ${e.message}", e)
                        call.respond(
                            HttpStatusCode.InternalServerError,
                            mapOf("error" to e.message)
                        )
                    }
                }
                
                // Delete session
                delete("/{sessionId}") {
                    try {
                        val sessionId = call.parameters["sessionId"]
                            ?: return@delete call.respond(HttpStatusCode.BadRequest, "Missing sessionId")
                        
                        val deleted = chatUseCases.deleteSession(sessionId)
                        if (deleted) {
                            call.respond(HttpStatusCode.NoContent)
                        } else {
                            call.respond(HttpStatusCode.NotFound, "Session not found")
                        }
                        
                    } catch (e: Exception) {
                        logger.error("Error deleting session: ${e.message}", e)
                        call.respond(
                            HttpStatusCode.InternalServerError,
                            mapOf("error" to e.message)
                        )
                    }
                }
            }
            
            // Health check endpoint
            get("/api/v1/health") {
                try {
                    val health = chatUseCases.healthCheck()
                    call.respond(HttpStatusCode.OK, health)
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.ServiceUnavailable,
                        mapOf("status" to "unhealthy", "error" to e.message)
                    )
                }
            }
        }
    }
}
