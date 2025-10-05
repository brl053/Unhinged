package com.unhinged.services.cdc

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import com.unhinged.cdc.minimal.MinimalEventProto
import io.ktor.server.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.Channel
import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.clients.producer.KafkaProducer
import org.apache.kafka.clients.producer.ProducerConfig
import org.apache.kafka.clients.producer.ProducerRecord
import org.apache.kafka.common.serialization.ByteArrayDeserializer
import org.apache.kafka.common.serialization.ByteArraySerializer
import org.apache.kafka.common.serialization.StringDeserializer
import org.apache.kafka.common.serialization.StringSerializer
import org.slf4j.LoggerFactory
import java.sql.Connection
import java.sql.DriverManager
import java.time.Duration
import java.util.*
import java.util.concurrent.ConcurrentHashMap

/**
 * Minimal CDC Service - Single class handling producer, consumer, and WebSocket
 * MVP vertical slice for LLM inference events
 */
class CDCService {
    private val logger = LoggerFactory.getLogger(CDCService::class.java)
    private val objectMapper: ObjectMapper = jacksonObjectMapper()
    
    // Kafka configuration
    private val kafkaBootstrapServers = "localhost:9092"
    private val topicName = "llm-events"
    
    // PostgreSQL configuration
    private val dbUrl = "jdbc:postgresql://localhost:5432/unhinged_cdc"
    private val dbUser = "postgres"
    private val dbPassword = "postgres"
    
    // WebSocket connections for real-time event streaming
    private val webSocketSessions = ConcurrentHashMap<String, DefaultWebSocketSession>()
    private val eventChannel = Channel<String>(Channel.UNLIMITED)
    
    // Kafka producer (lazy initialization)
    private val producer: KafkaProducer<String, ByteArray> by lazy {
        val props = Properties().apply {
            put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaBootstrapServers)
            put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer::class.java.name)
            put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, ByteArraySerializer::class.java.name)
            put(ProducerConfig.ACKS_CONFIG, "1")
            put(ProducerConfig.RETRIES_CONFIG, 3)
            put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true)
        }
        KafkaProducer(props)
    }
    
    // Kafka consumer (lazy initialization)
    private val consumer: KafkaConsumer<String, ByteArray> by lazy {
        val props = Properties().apply {
            put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaBootstrapServers)
            put(ConsumerConfig.GROUP_ID_CONFIG, "cdc-consumer-group")
            put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer::class.java.name)
            put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, ByteArrayDeserializer::class.java.name)
            put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest")
            put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, true)
        }
        KafkaConsumer(props)
    }
    
    /**
     * Start the CDC service (consumer + WebSocket broadcaster)
     */
    fun start() {
        logger.info("🚀 Starting CDC Service...")
        
        // Start Kafka consumer in background
        GlobalScope.launch {
            startConsumer()
        }
        
        // Start WebSocket broadcaster
        GlobalScope.launch {
            startWebSocketBroadcaster()
        }
        
        logger.info("✅ CDC Service started")
    }
    
    /**
     * Produce LLM inference event to Kafka
     */
    suspend fun produceLLMInferenceEvent(
        prompt: String,
        response: String,
        model: String,
        promptTokens: Int,
        responseTokens: Int,
        latencyMs: Long,
        success: Boolean,
        errorMessage: String? = null,
        intent: String,
        confidence: Float,
        userId: String,
        sessionId: String
    ) {
        try {
            // Create protobuf event
            val llmEvent = MinimalEventProto.LLMInferenceEvent.newBuilder()
                .setPrompt(prompt)
                .setResponse(response)
                .setModel(model)
                .setPromptTokens(promptTokens)
                .setResponseTokens(responseTokens)
                .setLatencyMs(latencyMs)
                .setSuccess(success)
                .setErrorMessage(errorMessage ?: "")
                .setIntent(intent)
                .setConfidence(confidence)
                .build()
            
            // Create universal event envelope
            val universalEvent = MinimalEventProto.UniversalEvent.newBuilder()
                .setEventId(UUID.randomUUID().toString())
                .setEventType("llm.inference.completed")
                .setTimestampMs(System.currentTimeMillis())
                .setUserId(userId)
                .setSessionId(sessionId)
                .setPayload(llmEvent.toByteString())
                .build()
            
            // Send to Kafka
            val record = ProducerRecord(
                topicName,
                universalEvent.eventId,
                universalEvent.toByteArray()
            )
            
            producer.send(record) { metadata, exception ->
                if (exception != null) {
                    logger.error("❌ Failed to send event to Kafka", exception)
                } else {
                    logger.info("📤 Event sent to Kafka: ${universalEvent.eventId} (offset: ${metadata.offset()})")
                }
            }
            
        } catch (e: Exception) {
            logger.error("❌ Failed to produce LLM inference event", e)
            throw e
        }
    }
    
    /**
     * Start Kafka consumer
     */
    private suspend fun startConsumer() {
        try {
            consumer.subscribe(listOf(topicName))
            logger.info("📥 Kafka consumer subscribed to topic: $topicName")
            
            while (true) {
                val records = consumer.poll(Duration.ofMillis(1000))
                
                for (record in records) {
                    try {
                        // Deserialize protobuf event
                        val universalEvent = MinimalEventProto.UniversalEvent.parseFrom(record.value())
                        
                        // Store in PostgreSQL
                        storeEventInDatabase(universalEvent)
                        
                        // Send to WebSocket clients
                        val eventJson = convertEventToJson(universalEvent)
                        eventChannel.send(eventJson)
                        
                        logger.info("✅ Processed event: ${universalEvent.eventId}")
                        
                    } catch (e: Exception) {
                        logger.error("❌ Failed to process Kafka record", e)
                    }
                }
            }
        } catch (e: Exception) {
            logger.error("❌ Kafka consumer error", e)
        }
    }
    
    /**
     * Store event in PostgreSQL
     */
    private fun storeEventInDatabase(event: MinimalEventProto.UniversalEvent) {
        try {
            DriverManager.getConnection(dbUrl, dbUser, dbPassword).use { connection ->
                val sql = """
                    INSERT INTO events (event_id, event_type, timestamp_ms, user_id, session_id, payload)
                    VALUES (?, ?, ?, ?, ?, ?::jsonb)
                """.trimIndent()
                
                connection.prepareStatement(sql).use { statement ->
                    statement.setString(1, event.eventId)
                    statement.setString(2, event.eventType)
                    statement.setLong(3, event.timestampMs)
                    statement.setString(4, event.userId)
                    statement.setString(5, event.sessionId)
                    statement.setString(6, convertEventToJson(event))
                    
                    statement.executeUpdate()
                }
            }
            
            logger.debug("💾 Event stored in database: ${event.eventId}")
            
        } catch (e: Exception) {
            logger.error("❌ Failed to store event in database", e)
            throw e
        }
    }
    
    /**
     * Convert protobuf event to JSON for storage and WebSocket
     */
    private fun convertEventToJson(event: MinimalEventProto.UniversalEvent): String {
        try {
            // Parse the LLM inference event from payload
            val llmEvent = MinimalEventProto.LLMInferenceEvent.parseFrom(event.payload)
            
            val eventMap = mapOf(
                "event_id" to event.eventId,
                "event_type" to event.eventType,
                "timestamp_ms" to event.timestampMs,
                "user_id" to event.userId,
                "session_id" to event.sessionId,
                "payload" to mapOf(
                    "prompt" to llmEvent.prompt,
                    "response" to llmEvent.response,
                    "model" to llmEvent.model,
                    "prompt_tokens" to llmEvent.promptTokens,
                    "response_tokens" to llmEvent.responseTokens,
                    "latency_ms" to llmEvent.latencyMs,
                    "success" to llmEvent.success,
                    "error_message" to llmEvent.errorMessage,
                    "intent" to llmEvent.intent,
                    "confidence" to llmEvent.confidence
                )
            )
            
            return objectMapper.writeValueAsString(eventMap)
            
        } catch (e: Exception) {
            logger.error("❌ Failed to convert event to JSON", e)
            return "{\"error\": \"Failed to parse event\"}"
        }
    }
    
    /**
     * Start WebSocket broadcaster
     */
    private suspend fun startWebSocketBroadcaster() {
        logger.info("📡 Starting WebSocket broadcaster...")
        
        for (eventJson in eventChannel) {
            // Broadcast to all connected WebSocket clients
            val disconnectedSessions = mutableListOf<String>()
            
            webSocketSessions.forEach { (sessionId, session) ->
                try {
                    session.send(Frame.Text(eventJson))
                } catch (e: Exception) {
                    logger.warn("⚠️ Failed to send to WebSocket session $sessionId", e)
                    disconnectedSessions.add(sessionId)
                }
            }
            
            // Clean up disconnected sessions
            disconnectedSessions.forEach { sessionId ->
                webSocketSessions.remove(sessionId)
                logger.info("🔌 Removed disconnected WebSocket session: $sessionId")
            }
        }
    }
    
    /**
     * Add WebSocket session for real-time event streaming
     */
    fun addWebSocketSession(sessionId: String, session: DefaultWebSocketSession) {
        webSocketSessions[sessionId] = session
        logger.info("🔌 Added WebSocket session: $sessionId")
    }
    
    /**
     * Remove WebSocket session
     */
    fun removeWebSocketSession(sessionId: String) {
        webSocketSessions.remove(sessionId)
        logger.info("🔌 Removed WebSocket session: $sessionId")
    }
    
    /**
     * Get recent events from database (for initial load)
     */
    fun getRecentEvents(limit: Int = 50): List<Map<String, Any>> {
        try {
            DriverManager.getConnection(dbUrl, dbUser, dbPassword).use { connection ->
                val sql = """
                    SELECT event_id, event_type, timestamp_ms, user_id, session_id, payload, created_at
                    FROM events
                    ORDER BY timestamp_ms DESC
                    LIMIT ?
                """.trimIndent()
                
                connection.prepareStatement(sql).use { statement ->
                    statement.setInt(1, limit)
                    
                    val resultSet = statement.executeQuery()
                    val events = mutableListOf<Map<String, Any>>()
                    
                    while (resultSet.next()) {
                        events.add(mapOf(
                            "event_id" to resultSet.getString("event_id"),
                            "event_type" to resultSet.getString("event_type"),
                            "timestamp_ms" to resultSet.getLong("timestamp_ms"),
                            "user_id" to resultSet.getString("user_id"),
                            "session_id" to resultSet.getString("session_id"),
                            "payload" to objectMapper.readValue(resultSet.getString("payload"), Map::class.java),
                            "created_at" to resultSet.getTimestamp("created_at").toString()
                        ))
                    }
                    
                    return events
                }
            }
        } catch (e: Exception) {
            logger.error("❌ Failed to get recent events", e)
            return emptyList()
        }
    }
    
    /**
     * Shutdown the CDC service
     */
    fun shutdown() {
        logger.info("🛑 Shutting down CDC Service...")
        
        try {
            producer.close()
            consumer.close()
            eventChannel.close()
            webSocketSessions.clear()
        } catch (e: Exception) {
            logger.error("❌ Error during CDC service shutdown", e)
        }
        
        logger.info("✅ CDC Service shutdown complete")
    }
}
