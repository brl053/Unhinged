// ============================================================================
// Chat Repository - Infrastructure Contracts
// ============================================================================
//
// @file ChatRepository.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description Repository interfaces for chat domain
// ============================================================================

package com.unhinged.infrastructure.chat

import com.unhinged.domain.chat.ChatMessage
import com.unhinged.domain.chat.ChatSession

/**
 * Repository interface for chat messages
 * Implementation can be in-memory, database, or any other storage
 */
interface ChatMessageRepository {
    
    suspend fun save(message: ChatMessage): ChatMessage
    
    suspend fun findById(id: String): ChatMessage?
    
    suspend fun findBySessionId(sessionId: String, limit: Int = 50): List<ChatMessage>
    
    suspend fun findBySessionIdSince(
        sessionId: String, 
        since: String, 
        limit: Int = 50
    ): List<ChatMessage>
    
    suspend fun deleteById(id: String): Boolean
    
    suspend fun deleteBySessionId(sessionId: String): Int
}

/**
 * Repository interface for chat sessions
 */
interface ChatSessionRepository {
    
    suspend fun save(session: ChatSession): ChatSession
    
    suspend fun findById(id: String): ChatSession?
    
    suspend fun findByUserId(userId: String, limit: Int = 20): List<ChatSession>
    
    suspend fun findActiveByUserId(userId: String, limit: Int = 20): List<ChatSession>
    
    suspend fun updateSession(session: ChatSession): ChatSession?
    
    suspend fun deactivateSession(sessionId: String): Boolean
    
    suspend fun deleteById(id: String): Boolean
}

/**
 * Simple in-memory implementation for development
 */
class InMemoryChatMessageRepository : ChatMessageRepository {
    
    private val messages = mutableMapOf<String, ChatMessage>()
    private val sessionMessages = mutableMapOf<String, MutableList<String>>()
    
    override suspend fun save(message: ChatMessage): ChatMessage {
        messages[message.id] = message
        sessionMessages.getOrPut(message.sessionId) { mutableListOf() }.add(message.id)
        return message
    }
    
    override suspend fun findById(id: String): ChatMessage? {
        return messages[id]
    }
    
    override suspend fun findBySessionId(sessionId: String, limit: Int): List<ChatMessage> {
        return sessionMessages[sessionId]
            ?.mapNotNull { messages[it] }
            ?.sortedBy { it.timestamp }
            ?.takeLast(limit)
            ?: emptyList()
    }
    
    override suspend fun findBySessionIdSince(
        sessionId: String, 
        since: String, 
        limit: Int
    ): List<ChatMessage> {
        return findBySessionId(sessionId, limit)
            .filter { it.timestamp > since }
    }
    
    override suspend fun deleteById(id: String): Boolean {
        val message = messages.remove(id)
        if (message != null) {
            sessionMessages[message.sessionId]?.remove(id)
            return true
        }
        return false
    }
    
    override suspend fun deleteBySessionId(sessionId: String): Int {
        val messageIds = sessionMessages.remove(sessionId) ?: return 0
        var deletedCount = 0
        messageIds.forEach { id ->
            if (messages.remove(id) != null) {
                deletedCount++
            }
        }
        return deletedCount
    }
}

/**
 * Simple in-memory implementation for development
 */
class InMemoryChatSessionRepository : ChatSessionRepository {
    
    private val sessions = mutableMapOf<String, ChatSession>()
    private val userSessions = mutableMapOf<String, MutableList<String>>()
    
    override suspend fun save(session: ChatSession): ChatSession {
        sessions[session.id] = session
        userSessions.getOrPut(session.userId) { mutableListOf() }.add(session.id)
        return session
    }
    
    override suspend fun findById(id: String): ChatSession? {
        return sessions[id]
    }
    
    override suspend fun findByUserId(userId: String, limit: Int): List<ChatSession> {
        return userSessions[userId]
            ?.mapNotNull { sessions[it] }
            ?.sortedByDescending { it.updatedAt }
            ?.take(limit)
            ?: emptyList()
    }
    
    override suspend fun findActiveByUserId(userId: String, limit: Int): List<ChatSession> {
        return findByUserId(userId, limit)
            .filter { it.isActive }
    }
    
    override suspend fun updateSession(session: ChatSession): ChatSession? {
        return if (sessions.containsKey(session.id)) {
            sessions[session.id] = session
            session
        } else {
            null
        }
    }
    
    override suspend fun deactivateSession(sessionId: String): Boolean {
        val session = sessions[sessionId]
        return if (session != null) {
            sessions[sessionId] = session.copy(isActive = false)
            true
        } else {
            false
        }
    }
    
    override suspend fun deleteById(id: String): Boolean {
        val session = sessions.remove(id)
        if (session != null) {
            userSessions[session.userId]?.remove(id)
            return true
        }
        return false
    }
}
