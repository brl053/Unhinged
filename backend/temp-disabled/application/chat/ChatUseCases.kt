// ============================================================================
// Chat Use Cases - Application Layer
// ============================================================================
//
// @file ChatUseCases.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Application use cases for chat functionality
// ============================================================================

package com.unhinged.application.chat

import com.unhinged.domain.chat.*
import com.unhinged.infrastructure.chat.ChatMessageRepository
import com.unhinged.infrastructure.chat.ChatSessionRepository
import kotlinx.serialization.Serializable
import java.time.Instant

/**
 * Data Transfer Objects for use cases
 */
@Serializable
data class SendMessageRequest(
    val content: String,
    val sessionId: String,
    val userId: String,
    val metadata: Map<String, String> = emptyMap()
)

@Serializable
data class SendMessageResponse(
    val userMessage: ChatMessage,
    val assistantMessage: ChatMessage,
    val processingTimeMs: Long
)

@Serializable
data class CreateSessionRequest(
    val userId: String,
    val title: String? = null,
    val metadata: Map<String, String> = emptyMap()
)

@Serializable
data class GetConversationRequest(
    val sessionId: String,
    val limit: Int = 50,
    val since: String? = null
)

@Serializable
data class GetConversationResponse(
    val sessionId: String,
    val messages: List<ChatMessage>,
    val totalCount: Int
)

/**
 * Main chat use cases
 */
class ChatUseCases(
    private val messageRepository: ChatMessageRepository,
    private val sessionRepository: ChatSessionRepository,
    private val domainService: ChatDomainService = ChatDomainService()
) {
    
    /**
     * Send a message and get an AI response
     */
    suspend fun sendMessage(request: SendMessageRequest): SendMessageResponse {
        val startTime = System.currentTimeMillis()
        
        // Validate session exists
        val session = sessionRepository.findById(request.sessionId)
            ?: throw IllegalArgumentException("Session not found: ${request.sessionId}")
        
        if (!session.isActive) {
            throw IllegalArgumentException("Session is not active: ${request.sessionId}")
        }
        
        // Create user message
        val userMessage = domainService.createMessage(
            content = request.content,
            role = MessageRole.USER,
            sessionId = request.sessionId,
            metadata = request.metadata
        )
        
        // Save user message
        messageRepository.save(userMessage)
        
        // Get conversation history for context
        val conversationHistory = messageRepository.findBySessionId(request.sessionId, 20)
        
        // Generate AI response
        val responseContent = domainService.generateContextualResponse(
            userMessage = request.content,
            conversationHistory = conversationHistory
        )
        
        // Create assistant message
        val assistantMessage = domainService.createMessage(
            content = responseContent,
            role = MessageRole.ASSISTANT,
            sessionId = request.sessionId,
            metadata = mapOf(
                "model" to "unhinged-mock-v1",
                "context_length" to conversationHistory.size.toString()
            )
        )
        
        // Save assistant message
        messageRepository.save(assistantMessage)
        
        // Update session timestamp
        sessionRepository.updateSession(
            session.copy(updatedAt = Instant.now().toString())
        )
        
        val processingTime = System.currentTimeMillis() - startTime
        
        return SendMessageResponse(
            userMessage = userMessage,
            assistantMessage = assistantMessage,
            processingTimeMs = processingTime
        )
    }
    
    /**
     * Create a new chat session
     */
    suspend fun createSession(request: CreateSessionRequest): ChatSession {
        val session = domainService.createSession(
            userId = request.userId,
            title = request.title,
            metadata = request.metadata
        )
        
        return sessionRepository.save(session)
    }
    
    /**
     * Get conversation history
     */
    suspend fun getConversation(request: GetConversationRequest): GetConversationResponse {
        val messages = if (request.since != null) {
            messageRepository.findBySessionIdSince(
                sessionId = request.sessionId,
                since = request.since,
                limit = request.limit
            )
        } else {
            messageRepository.findBySessionId(
                sessionId = request.sessionId,
                limit = request.limit
            )
        }
        
        return GetConversationResponse(
            sessionId = request.sessionId,
            messages = messages,
            totalCount = messages.size
        )
    }
    
    /**
     * Get user's chat sessions
     */
    suspend fun getUserSessions(userId: String, limit: Int = 20): List<ChatSession> {
        return sessionRepository.findActiveByUserId(userId, limit)
    }
    
    /**
     * Get a specific session
     */
    suspend fun getSession(sessionId: String): ChatSession? {
        return sessionRepository.findById(sessionId)
    }
    
    /**
     * Deactivate a session
     */
    suspend fun deactivateSession(sessionId: String): Boolean {
        return sessionRepository.deactivateSession(sessionId)
    }
    
    /**
     * Delete a session and all its messages
     */
    suspend fun deleteSession(sessionId: String): Boolean {
        val deletedMessages = messageRepository.deleteBySessionId(sessionId)
        val deletedSession = sessionRepository.deleteById(sessionId)
        return deletedSession && deletedMessages >= 0
    }
    
    /**
     * Health check for the chat system
     */
    suspend fun healthCheck(): Map<String, Any> {
        return mapOf(
            "status" to "healthy",
            "service" to "chat-use-cases",
            "timestamp" to Instant.now().toString(),
            "version" to "1.0.0"
        )
    }
}
