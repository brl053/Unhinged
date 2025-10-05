// ============================================================================
// Chat Domain - Core Business Logic
// ============================================================================
//
// @file ChatDomain.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Pure domain logic for chat functionality
// ============================================================================

package com.unhinged.domain.chat

import kotlinx.serialization.Serializable
import java.time.Instant
import java.util.UUID

/**
 * Core chat domain entities and value objects
 */

@Serializable
data class ChatMessage(
    val id: String = UUID.randomUUID().toString(),
    val content: String,
    val role: MessageRole,
    val timestamp: String = Instant.now().toString(),
    val sessionId: String,
    val metadata: Map<String, String> = emptyMap()
) {
    init {
        require(content.isNotBlank()) { "Message content cannot be blank" }
        require(sessionId.isNotBlank()) { "Session ID cannot be blank" }
    }
}

@Serializable
enum class MessageRole {
    USER,
    ASSISTANT,
    SYSTEM
}

@Serializable
data class ChatSession(
    val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val title: String? = null,
    val createdAt: String = Instant.now().toString(),
    val updatedAt: String = Instant.now().toString(),
    val isActive: Boolean = true,
    val metadata: Map<String, String> = emptyMap()
) {
    init {
        require(userId.isNotBlank()) { "User ID cannot be blank" }
    }
}

/**
 * Domain services - pure business logic
 */
class ChatDomainService {
    
    /**
     * Create a new chat message with validation
     */
    fun createMessage(
        content: String,
        role: MessageRole,
        sessionId: String,
        metadata: Map<String, String> = emptyMap()
    ): ChatMessage {
        return ChatMessage(
            content = content.trim(),
            role = role,
            sessionId = sessionId,
            metadata = metadata
        )
    }
    
    /**
     * Create a new chat session
     */
    fun createSession(
        userId: String,
        title: String? = null,
        metadata: Map<String, String> = emptyMap()
    ): ChatSession {
        return ChatSession(
            userId = userId,
            title = title?.trim(),
            metadata = metadata
        )
    }
    
    /**
     * Generate a contextual response based on conversation history
     */
    fun generateContextualResponse(
        userMessage: String,
        conversationHistory: List<ChatMessage>,
        maxHistoryLength: Int = 10
    ): String {
        // Simple contextual response generation
        val recentHistory = conversationHistory
            .takeLast(maxHistoryLength)
            .filter { it.role != MessageRole.SYSTEM }
        
        return when {
            userMessage.contains("hello", ignoreCase = true) || 
            userMessage.contains("hi", ignoreCase = true) -> {
                if (recentHistory.isEmpty()) {
                    "Hello! I'm Unhinged AI. How can I help you today?"
                } else {
                    "Hello again! What would you like to discuss?"
                }
            }
            
            userMessage.contains("how are you", ignoreCase = true) -> 
                "I'm doing well, thank you! I'm here and ready to help with whatever you need."
            
            userMessage.contains("what", ignoreCase = true) && userMessage.contains("?") -> 
                "That's an interesting question! Let me think about that... ${generateContextualInsight(recentHistory)}"
            
            userMessage.contains("why", ignoreCase = true) -> 
                "Great question! The reasoning involves several factors... ${generateContextualInsight(recentHistory)}"
            
            userMessage.contains("help", ignoreCase = true) -> 
                "I'd be happy to help! Based on our conversation, I can assist you with ${generateHelpSuggestion(recentHistory)}"
            
            userMessage.length > 100 -> 
                "That's quite a detailed message! Let me break this down: ${generateDetailedResponse(userMessage, recentHistory)}"
            
            recentHistory.isNotEmpty() -> 
                "Building on our previous discussion, ${generateContinuationResponse(recentHistory)}"
            
            else -> generateGenericResponse()
        }
    }
    
    private fun generateContextualInsight(history: List<ChatMessage>): String {
        return if (history.isNotEmpty()) {
            val topics = extractTopics(history)
            if (topics.isNotEmpty()) {
                "Given our discussion about ${topics.joinToString(", ")}, I think..."
            } else {
                "Based on our conversation so far..."
            }
        } else {
            "From a general perspective..."
        }
    }
    
    private fun generateHelpSuggestion(history: List<ChatMessage>): String {
        val topics = extractTopics(history)
        return if (topics.isNotEmpty()) {
            "${topics.first()} and related topics."
        } else {
            "a wide range of topics and questions."
        }
    }
    
    private fun generateDetailedResponse(message: String, history: List<ChatMessage>): String {
        val keyPoints = message.split(Regex("[.!?]")).take(3)
        return "You've raised several important points: ${keyPoints.joinToString("; ")}. Let me address each one..."
    }
    
    private fun generateContinuationResponse(history: List<ChatMessage>): String {
        val lastUserMessage = history.lastOrNull { it.role == MessageRole.USER }
        return if (lastUserMessage != null) {
            "continuing from your point about '${lastUserMessage.content.take(50)}...'"
        } else {
            "I can elaborate further on what we were discussing."
        }
    }
    
    private fun generateGenericResponse(): String {
        val responses = listOf(
            "That's an interesting perspective! Let me share my thoughts...",
            "I see what you mean. Here's how I'd approach that...",
            "Great point! That opens up several possibilities...",
            "I appreciate your question. Here's my take on it...",
            "That's worth exploring in more detail. Consider this...",
            "Fascinating! That reminds me of an important concept...",
            "You've touched on something significant there...",
            "That's a thoughtful observation. Let me build on that..."
        )
        return responses.random()
    }
    
    private fun extractTopics(history: List<ChatMessage>): List<String> {
        // Simple topic extraction - in a real system, this would use NLP
        val commonTopics = listOf(
            "technology", "programming", "AI", "machine learning", "data",
            "business", "strategy", "design", "development", "architecture",
            "science", "research", "analysis", "optimization", "innovation"
        )
        
        val conversationText = history.joinToString(" ") { it.content.lowercase() }
        return commonTopics.filter { topic ->
            conversationText.contains(topic)
        }.take(3)
    }
}

/**
 * Domain events for chat operations
 */
@Serializable
sealed class ChatDomainEvent {
    abstract val timestamp: String
    abstract val sessionId: String
    
    @Serializable
    data class MessageCreated(
        val message: ChatMessage,
        override val timestamp: String = Instant.now().toString(),
        override val sessionId: String = message.sessionId
    ) : ChatDomainEvent()
    
    @Serializable
    data class SessionCreated(
        val session: ChatSession,
        override val timestamp: String = Instant.now().toString(),
        override val sessionId: String = session.id
    ) : ChatDomainEvent()
    
    @Serializable
    data class ResponseGenerated(
        val userMessageId: String,
        val responseMessage: ChatMessage,
        val processingTimeMs: Long,
        override val timestamp: String = Instant.now().toString(),
        override val sessionId: String = responseMessage.sessionId
    ) : ChatDomainEvent()
}
