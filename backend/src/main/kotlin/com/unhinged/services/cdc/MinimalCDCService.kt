package com.unhinged.services.cdc

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.module.kotlin.jacksonObjectMapper
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import io.ktor.server.websocket.*
import io.ktor.websocket.*
import kotlinx.coroutines.*
import kotlinx.coroutines.channels.Channel
import kotlinx.serialization.Serializable
import org.apache.kafka.clients.consumer.ConsumerConfig
import org.apache.kafka.clients.consumer.KafkaConsumer
import org.apache.kafka.clients.producer.KafkaProducer
import org.apache.kafka.clients.producer.ProducerConfig
import org.apache.kafka.clients.producer.ProducerRecord
import org.apache.kafka.common.serialization.*
import org.slf4j.LoggerFactory
import java.sql.DriverManager
import java.time.Duration
import java.util.*
import java.util.concurrent.ConcurrentHashMap

/**
 * Minimal CDC Service - MVP Vertical Slice
 * 
 * Single class handling:
 * - LLM inference with event production
 * - Kafka consumer for event storage
 * - WebSocket for real-time event streaming
 * - PostgreSQL storage
 */
class MinimalCDCService {
    private val logger = LoggerFactory.getLogger(MinimalCDCService::class.java)
    private val objectMapper: ObjectMapper = jacksonObjectMapper()
    
    // Configuration
    private val kafkaBootstrapServers = "localhost:9092"
    private val topicName = "llm-events"
    private val dbUrl = "jdbc:postgresql://localhost:5432/unhinged"
    private val dbUser = "postgres"
    private val dbPassword = "postgres"
    private val ollamaUrl = "http://localhost:11434"

    // HTTP client for Ollama
    private val httpClient = HttpClient(CIO) {
        install(ContentNegotiation) {
            json()
        }
    }
    
    // WebSocket connections
    private val webSocketSessions = ConcurrentHashMap<String, DefaultWebSocketSession>()
    private val eventChannel = Channel<String>(Channel.UNLIMITED)
    
    // Kafka producer
    private val producer: KafkaProducer<String, String> by lazy {
        val props = Properties().apply {
            put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaBootstrapServers)
            put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer::class.java.name)
            put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer::class.java.name)
            put(ProducerConfig.ACKS_CONFIG, "1")
            put(ProducerConfig.RETRIES_CONFIG, 3)
        }
        KafkaProducer(props)
    }
    
    // Kafka consumer
    private val consumer: KafkaConsumer<String, String> by lazy {
        val props = Properties().apply {
            put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, kafkaBootstrapServers)
            put(ConsumerConfig.GROUP_ID_CONFIG, "cdc-consumer")
            put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer::class.java.name)
            put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer::class.java.name)
            put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "latest")
        }
        KafkaConsumer(props)
    }
    
    @Serializable
    data class LLMInferenceRequest(
        val prompt: String,
        val model: String = "llama3.2",
        val userId: String = "user-1",
        val sessionId: String = "session-1"
    )

    @Serializable
    data class OllamaRequest(
        val model: String,
        val prompt: String,
        val stream: Boolean = false
    )

    @Serializable
    data class OllamaResponse(
        val response: String,
        val done: Boolean = true,
        val context: List<Int>? = null,
        val total_duration: Long? = null,
        val load_duration: Long? = null,
        val prompt_eval_count: Int? = null,
        val prompt_eval_duration: Long? = null,
        val eval_count: Int? = null,
        val eval_duration: Long? = null
    )
    
    @Serializable
    data class LLMInferenceResponse(
        val response: String,
        val model: String,
        val promptTokens: Int,
        val responseTokens: Int,
        val latencyMs: Long,
        val eventId: String
    )
    
    @Serializable
    data class UniversalEvent(
        val eventId: String,
        val eventType: String,
        val timestampMs: Long,
        val userId: String,
        val sessionId: String,
        val payload: LLMInferenceEvent
    )
    
    @Serializable
    data class LLMInferenceEvent(
        val prompt: String,
        val response: String,
        val model: String,
        val promptTokens: Int,
        val responseTokens: Int,
        val latencyMs: Long,
        val success: Boolean,
        val errorMessage: String = "",
        val intent: String,
        val confidence: Float
    )
    
    /**
     * Start the CDC service
     */
    fun start() {
        logger.info("🚀 Starting Minimal CDC Service...")
        
        // Start Kafka consumer
        GlobalScope.launch {
            startConsumer()
        }
        
        // Start WebSocket broadcaster
        GlobalScope.launch {
            startWebSocketBroadcaster()
        }
        
        logger.info("✅ Minimal CDC Service started")
    }
    
    /**
     * Configure Ktor routes
     */
    fun configureRoutes(application: Application) {
        application.routing {
            // Health check endpoints
            get("/health") {
                val ollamaHealth = checkOllamaHealth()
                call.respond(mapOf(
                    "status" to "healthy",
                    "timestamp" to System.currentTimeMillis(),
                    "services" to mapOf(
                        "kafka" to checkKafkaHealth(),
                        "database" to checkDatabaseHealth(),
                        "ollama" to ollamaHealth
                    )
                ))
            }

            get("/ping") {
                call.respond(mapOf("message" to "pong", "timestamp" to System.currentTimeMillis()))
            }
            // LLM inference endpoint with CDC
            post("/api/llm/infer") {
                try {
                    val request = call.receive<LLMInferenceRequest>()
                    val startTime = System.currentTimeMillis()

                    // Real Ollama inference
                    val response = callOllama(request.prompt, request.model)
                    val endTime = System.currentTimeMillis()
                    val latencyMs = endTime - startTime
                    
                    // Create and produce CDC event
                    val eventId = UUID.randomUUID().toString()
                    val event = createLLMInferenceEvent(
                        eventId = eventId,
                        prompt = request.prompt,
                        response = response,
                        model = request.model,
                        promptTokens = request.prompt.split(" ").size,
                        responseTokens = response.split(" ").size,
                        latencyMs = latencyMs,
                        success = true,
                        intent = "User requested information",
                        confidence = 0.85f,
                        userId = request.userId,
                        sessionId = request.sessionId
                    )
                    
                    // Send to Kafka
                    produceEvent(event)
                    
                    // Return response
                    call.respond(LLMInferenceResponse(
                        response = response,
                        model = request.model,
                        promptTokens = request.prompt.split(" ").size,
                        responseTokens = response.split(" ").size,
                        latencyMs = latencyMs,
                        eventId = eventId
                    ))
                    
                } catch (e: Exception) {
                    logger.error("❌ LLM inference failed", e)
                    call.respond(mapOf("error" to "Inference failed: ${e.message}"))
                }
            }
            
            // Get recent events
            get("/api/events") {
                try {
                    val events = getRecentEvents()
                    call.respond(events)
                } catch (e: Exception) {
                    logger.error("❌ Failed to get events", e)
                    call.respond(mapOf("error" to "Failed to get events"))
                }
            }
            
            // WebSocket for real-time events
            webSocket("/api/events/stream") {
                val sessionId = UUID.randomUUID().toString()
                webSocketSessions[sessionId] = this
                logger.info("🔌 WebSocket connected: $sessionId")
                
                try {
                    for (frame in incoming) {
                        // Handle incoming messages if needed
                    }
                } catch (e: Exception) {
                    logger.warn("⚠️ WebSocket error: $sessionId", e)
                } finally {
                    webSocketSessions.remove(sessionId)
                    logger.info("🔌 WebSocket disconnected: $sessionId")
                }
            }
        }
    }
    
    /**
     * Call Ollama for LLM inference
     */
    private suspend fun callOllama(prompt: String, model: String): String {
        return try {
            logger.info("🤖 Calling Ollama: model=$model, prompt=${prompt.take(50)}...")

            val ollamaRequest = OllamaRequest(
                model = model,
                prompt = prompt,
                stream = false
            )

            val response = httpClient.post("$ollamaUrl/api/generate") {
                contentType(ContentType.Application.Json)
                setBody(ollamaRequest)
                timeout {
                    requestTimeoutMillis = 30000 // 30 second timeout
                }
            }

            if (response.status == HttpStatusCode.OK) {
                val ollamaResponse = response.body<OllamaResponse>()
                logger.info("✅ Ollama response received: ${ollamaResponse.response.take(100)}...")
                ollamaResponse.response
            } else {
                val errorMsg = "Ollama request failed with status: ${response.status}"
                logger.error("❌ $errorMsg")
                "Error: $errorMsg"
            }

        } catch (e: Exception) {
            val errorMsg = "Failed to call Ollama: ${e.message}"
            logger.error("❌ $errorMsg", e)
            "Error: $errorMsg"
        }
    }
    
    /**
     * Create LLM inference event
     */
    private fun createLLMInferenceEvent(
        eventId: String,
        prompt: String,
        response: String,
        model: String,
        promptTokens: Int,
        responseTokens: Int,
        latencyMs: Long,
        success: Boolean,
        intent: String,
        confidence: Float,
        userId: String,
        sessionId: String
    ): UniversalEvent {
        return UniversalEvent(
            eventId = eventId,
            eventType = "llm.inference.completed",
            timestampMs = System.currentTimeMillis(),
            userId = userId,
            sessionId = sessionId,
            payload = LLMInferenceEvent(
                prompt = prompt,
                response = response,
                model = model,
                promptTokens = promptTokens,
                responseTokens = responseTokens,
                latencyMs = latencyMs,
                success = success,
                intent = intent,
                confidence = confidence
            )
        )
    }
    
    /**
     * Produce event to Kafka
     */
    private fun produceEvent(event: UniversalEvent) {
        try {
            val eventJson = objectMapper.writeValueAsString(event)
            val record = ProducerRecord(topicName, event.eventId, eventJson)
            
            producer.send(record) { metadata, exception ->
                if (exception != null) {
                    logger.error("❌ Failed to send event to Kafka", exception)
                } else {
                    logger.info("📤 Event sent to Kafka: ${event.eventId}")
                }
            }
        } catch (e: Exception) {
            logger.error("❌ Failed to produce event", e)
        }
    }
    
    /**
     * Start Kafka consumer
     */
    private suspend fun startConsumer() {
        try {
            consumer.subscribe(listOf(topicName))
            logger.info("📥 Kafka consumer subscribed to: $topicName")
            
            while (true) {
                val records = consumer.poll(Duration.ofMillis(1000))
                
                for (record in records) {
                    try {
                        val event = objectMapper.readValue(record.value(), UniversalEvent::class.java)
                        
                        // Store in PostgreSQL
                        storeEventInDatabase(event)
                        
                        // Send to WebSocket clients
                        eventChannel.send(record.value())
                        
                        logger.info("✅ Processed event: ${event.eventId}")
                        
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
    private fun storeEventInDatabase(event: UniversalEvent) {
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
                    statement.setString(6, objectMapper.writeValueAsString(event.payload))
                    
                    statement.executeUpdate()
                }
            }
            
            logger.debug("💾 Event stored: ${event.eventId}")
            
        } catch (e: Exception) {
            logger.error("❌ Failed to store event", e)
        }
    }
    
    /**
     * Start WebSocket broadcaster
     */
    private suspend fun startWebSocketBroadcaster() {
        logger.info("📡 Starting WebSocket broadcaster...")
        
        for (eventJson in eventChannel) {
            val disconnectedSessions = mutableListOf<String>()
            
            webSocketSessions.forEach { (sessionId, session) ->
                try {
                    session.send(Frame.Text(eventJson))
                } catch (e: Exception) {
                    disconnectedSessions.add(sessionId)
                }
            }
            
            disconnectedSessions.forEach { sessionId ->
                webSocketSessions.remove(sessionId)
            }
        }
    }
    
    /**
     * Check Kafka health
     */
    private fun checkKafkaHealth(): String {
        return try {
            // Simple check - try to list topics
            val adminClient = org.apache.kafka.clients.admin.AdminClient.create(
                mapOf("bootstrap.servers" to kafkaBootstrapServers)
            )
            val topics = adminClient.listTopics().names().get(java.time.Duration.ofSeconds(2))
            adminClient.close()
            if (topics.contains(topicName)) "healthy" else "topic_missing"
        } catch (e: Exception) {
            "unhealthy: ${e.message}"
        }
    }

    /**
     * Check database health
     */
    private fun checkDatabaseHealth(): String {
        return try {
            DriverManager.getConnection(dbUrl, dbUser, dbPassword).use { connection ->
                connection.prepareStatement("SELECT 1").use { statement ->
                    statement.executeQuery()
                }
            }
            "healthy"
        } catch (e: Exception) {
            "unhealthy: ${e.message}"
        }
    }

    /**
     * Check Ollama health
     */
    private suspend fun checkOllamaHealth(): String {
        return try {
            val response = httpClient.get("$ollamaUrl/api/tags") {
                timeout {
                    requestTimeoutMillis = 3000 // 3 second timeout
                }
            }
            if (response.status == HttpStatusCode.OK) "healthy" else "unhealthy: ${response.status}"
        } catch (e: Exception) {
            "unhealthy: ${e.message}"
        }
    }

    /**
     * Get recent events from database
     */
    private fun getRecentEvents(limit: Int = 50): List<Map<String, Any>> {
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
}
