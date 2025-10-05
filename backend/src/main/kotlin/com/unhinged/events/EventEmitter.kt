package com.unhinged.events

import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.transactions.transaction
import java.sql.Connection
import java.time.Instant
import java.util.*

/**
 * Simple fucking event emitter that writes structured events to PostgreSQL
 * with OpenTelemetry compliance and session-based querying for LLM context.
 */

@Serializable
data class UniversalEvent(
    val event_id: String = UUID.randomUUID().toString(),
    val event_type: String,
    val timestamp_ms: Long = Instant.now().toEpochMilli(),
    val trace_id: String,
    val user_id: String,
    val session_id: String,
    val payload: Map<String, String>
)

@Serializable
data class LLMInferenceEvent(
    val prompt: String,
    val response: String,
    val model: String,
    val prompt_tokens: Int,
    val response_tokens: Int,
    val latency_ms: Long,
    val success: Boolean,
    val error_message: String = "",
    val intent: String = "",
    val confidence: Double = 0.0
)

// Database table for events
object EventsTable : Table("events") {
    val event_id = varchar("event_id", 36).primaryKey()
    val event_type = varchar("event_type", 100)
    val timestamp_ms = long("timestamp_ms")
    val trace_id = varchar("trace_id", 36)
    val user_id = varchar("user_id", 100)
    val session_id = varchar("session_id", 100)
    val payload = text("payload") // JSON
    val created_at = timestamp("created_at").defaultExpression(CurrentTimestamp())
    
    // Indexes for fast querying
    init {
        index(false, session_id, timestamp_ms)
        index(false, user_id, timestamp_ms)
        index(false, trace_id)
        index(false, event_type, timestamp_ms)
    }
}

/**
 * The main event emitter - simple as fuck
 */
class EventEmitter(private val database: Database) {
    
    private val json = Json { ignoreUnknownKeys = true }
    
    /**
     * Emit an LLM inference event
     */
    fun emitLLMInference(
        traceId: String,
        userId: String,
        sessionId: String,
        event: LLMInferenceEvent
    ): String {
        val universalEvent = UniversalEvent(
            event_type = "llm.inference.completed",
            trace_id = traceId,
            user_id = userId,
            session_id = sessionId,
            payload = mapOf(
                "prompt" to event.prompt,
                "response" to event.response,
                "model" to event.model,
                "prompt_tokens" to event.prompt_tokens.toString(),
                "response_tokens" to event.response_tokens.toString(),
                "latency_ms" to event.latency_ms.toString(),
                "success" to event.success.toString(),
                "error_message" to event.error_message,
                "intent" to event.intent,
                "confidence" to event.confidence.toString()
            )
        )
        
        return emitEvent(universalEvent)
    }
    
    /**
     * Emit a generic event
     */
    fun emitEvent(
        eventType: String,
        traceId: String,
        userId: String,
        sessionId: String,
        payload: Map<String, String>
    ): String {
        val event = UniversalEvent(
            event_type = eventType,
            trace_id = traceId,
            user_id = userId,
            session_id = sessionId,
            payload = payload
        )
        
        return emitEvent(event)
    }
    
    /**
     * Emit a universal event - writes to PostgreSQL immediately
     */
    private fun emitEvent(event: UniversalEvent): String {
        transaction(database) {
            EventsTable.insert {
                it[event_id] = event.event_id
                it[event_type] = event.event_type
                it[timestamp_ms] = event.timestamp_ms
                it[trace_id] = event.trace_id
                it[user_id] = event.user_id
                it[session_id] = event.session_id
                it[payload] = json.encodeToString(UniversalEvent.serializer(), event)
            }
        }
        
        return event.event_id
    }
    
    /**
     * Get all events for a session (for LLM context)
     */
    fun getSessionEvents(sessionId: String, limit: Int = 100): List<UniversalEvent> {
        return transaction(database) {
            EventsTable
                .select { EventsTable.session_id eq sessionId }
                .orderBy(EventsTable.timestamp_ms, SortOrder.DESC)
                .limit(limit)
                .map { row ->
                    json.decodeFromString(
                        UniversalEvent.serializer(),
                        row[EventsTable.payload]
                    )
                }
        }
    }
    
    /**
     * Get events by trace ID (for debugging)
     */
    fun getTraceEvents(traceId: String): List<UniversalEvent> {
        return transaction(database) {
            EventsTable
                .select { EventsTable.trace_id eq traceId }
                .orderBy(EventsTable.timestamp_ms, SortOrder.ASC)
                .map { row ->
                    json.decodeFromString(
                        UniversalEvent.serializer(),
                        row[EventsTable.payload]
                    )
                }
        }
    }
    
    /**
     * Get recent events (for monitoring)
     */
    fun getRecentEvents(limit: Int = 50): List<UniversalEvent> {
        return transaction(database) {
            EventsTable
                .selectAll()
                .orderBy(EventsTable.timestamp_ms, SortOrder.DESC)
                .limit(limit)
                .map { row ->
                    json.decodeFromString(
                        UniversalEvent.serializer(),
                        row[EventsTable.payload]
                    )
                }
        }
    }
}

/**
 * Global event emitter instance
 */
object Events {
    private var emitter: EventEmitter? = null
    
    fun initialize(database: Database) {
        emitter = EventEmitter(database)
        
        // Create table if it doesn't exist
        transaction(database) {
            SchemaUtils.create(EventsTable)
        }
    }
    
    fun emit(): EventEmitter {
        return emitter ?: throw IllegalStateException("EventEmitter not initialized. Call Events.initialize() first.")
    }
}
