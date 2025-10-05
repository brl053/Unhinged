package com.unhinged.service

import kotlinx.serialization.*
import kotlinx.serialization.json.*
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap
import java.time.LocalDateTime
import java.util.UUID
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.http.*

/**
 * E-Tools Service - Backend service for dynamic tool management
 * Integrates with e-cli to provide platform-wide tool registry
 * Allows any LLM to discover, use, and create tools at runtime
 */

@Serializable
data class ToolDefinition(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val description: String,
    val category: String,
    val type: ToolType,
    val version: String = "1.0.0",
    val parameters: List<ToolParameter> = emptyList(),
    val returnType: String = "text",
    val executionType: ExecutionType = ExecutionType.SYNCHRONOUS,
    val endpoint: String? = null,
    val executable: String? = null,
    val metadata: ToolMetadata = ToolMetadata(),
    val createdAt: String = LocalDateTime.now().toString(),
    val updatedAt: String = LocalDateTime.now().toString()
)

@Serializable
data class ToolParameter(
    val name: String,
    val type: String,
    val description: String,
    val required: Boolean = true,
    val default: String? = null,
    val validation: ParameterValidation? = null
)

@Serializable
data class ParameterValidation(
    val pattern: String? = null,
    val minLength: Int? = null,
    val maxLength: Int? = null,
    val minValue: Double? = null,
    val maxValue: Double? = null,
    val allowedValues: List<String>? = null
)

@Serializable
enum class ToolType {
    @SerialName("local") LOCAL,
    @SerialName("platform") PLATFORM,
    @SerialName("remote") REMOTE,
    @SerialName("hybrid") HYBRID
}

@Serializable
enum class ExecutionType {
    @SerialName("synchronous") SYNCHRONOUS,
    @SerialName("asynchronous") ASYNCHRONOUS,
    @SerialName("streaming") STREAMING,
    @SerialName("batch") BATCH
}

@Serializable
data class ToolMetadata(
    val tags: List<String> = emptyList(),
    val author: String = "system",
    val dependencies: List<String> = emptyList(),
    val permissions: List<String> = emptyList(),
    val examples: List<ToolExample> = emptyList(),
    val documentation: String = "",
    val isPublic: Boolean = true,
    val isDeprecated: Boolean = false
)

@Serializable
data class ToolExample(
    val description: String,
    val input: Map<String, String>,
    val expectedOutput: String
)

@Serializable
data class ToolExecutionRequest(
    val toolId: String,
    val parameters: Map<String, String> = emptyMap(),
    val context: ExecutionContext = ExecutionContext(),
    val requestId: String = UUID.randomUUID().toString()
)

@Serializable
data class ExecutionContext(
    val userId: String? = null,
    val sessionId: String? = null,
    val llmModel: String? = null,
    val environment: String = "production",
    val timeout: Long = 30000,
    val metadata: Map<String, String> = emptyMap()
)

@Serializable
data class ToolExecutionResult(
    val requestId: String,
    val toolId: String,
    val success: Boolean,
    val result: String? = null,
    val error: String? = null,
    val executionTime: Long,
    val metadata: Map<String, String> = emptyMap(),
    val timestamp: String = LocalDateTime.now().toString()
)

@Serializable
data class ToolRegistryResponse(
    val tools: Map<String, ToolDefinition>,
    val categories: List<String>,
    val totalCount: Int,
    val metadata: Map<String, String> = emptyMap()
)

/**
 * Tools Service - Manages the platform-wide tool registry
 */
object ToolsService {
    private val tools = ConcurrentHashMap<String, ToolDefinition>()
    private val executionHistory = ConcurrentHashMap<String, ToolExecutionResult>()
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) { json() }
    }
    
    init {
        // Initialize with default platform tools
        initializeDefaultTools()
    }
    
    private fun initializeDefaultTools() {
        // LLM Query Tool
        val llmQueryTool = ToolDefinition(
            id = "llm-query",
            name = "LLM Query",
            description = "Query any LLM model running on the Unhinged Platform",
            category = "ai",
            type = ToolType.PLATFORM,
            endpoint = "/chat",
            parameters = listOf(
                ToolParameter(
                    name = "prompt",
                    type = "string",
                    description = "The prompt to send to the LLM",
                    required = true
                ),
                ToolParameter(
                    name = "model",
                    type = "string",
                    description = "LLM model to use",
                    required = false,
                    default = "openhermes"
                ),
                ToolParameter(
                    name = "temperature",
                    type = "float",
                    description = "Sampling temperature",
                    required = false,
                    default = "0.7"
                )
            ),
            metadata = ToolMetadata(
                tags = listOf("ai", "llm", "query"),
                author = "unhinged-platform",
                documentation = "Query LLM models running on the platform",
                examples = listOf(
                    ToolExample(
                        description = "Simple query",
                        input = mapOf("prompt" to "What is the weather?"),
                        expectedOutput = "AI-generated response about weather"
                    )
                )
            )
        )
        
        // TTS Tool
        val ttsTool = ToolDefinition(
            id = "text-to-speech",
            name = "Text to Speech",
            description = "Convert text to speech using the platform TTS service",
            category = "audio",
            type = ToolType.PLATFORM,
            endpoint = "/tts/synthesize",
            parameters = listOf(
                ToolParameter(
                    name = "text",
                    type = "string",
                    description = "Text to convert to speech",
                    required = true
                ),
                ToolParameter(
                    name = "language",
                    type = "string",
                    description = "Language code (e.g., 'en', 'es')",
                    required = false,
                    default = "en"
                )
            ),
            returnType = "binary",
            metadata = ToolMetadata(
                tags = listOf("audio", "tts", "speech"),
                author = "unhinged-platform",
                documentation = "Convert text to speech audio"
            )
        )
        
        registerTool(llmQueryTool)
        registerTool(ttsTool)
        
        println("[TOOLS-SERVICE] Initialized with ${tools.size} default tools")
    }
    
    // Tool registration and management
    fun registerTool(definition: ToolDefinition): Boolean {
        return try {
            tools[definition.id] = definition.copy(updatedAt = LocalDateTime.now().toString())
            println("[TOOLS-SERVICE] Registered tool: ${definition.name} (${definition.id})")
            true
        } catch (e: Exception) {
            println("[TOOLS-SERVICE] Failed to register tool ${definition.name}: ${e.message}")
            false
        }
    }
    
    fun unregisterTool(toolId: String): Boolean {
        return try {
            tools.remove(toolId)
            println("[TOOLS-SERVICE] Unregistered tool: $toolId")
            true
        } catch (e: Exception) {
            println("[TOOLS-SERVICE] Failed to unregister tool $toolId: ${e.message}")
            false
        }
    }
    
    fun getTool(toolId: String): ToolDefinition? = tools[toolId]
    
    fun getAllTools(): ToolRegistryResponse {
        val categories = tools.values.map { it.category }.distinct().sorted()
        return ToolRegistryResponse(
            tools = tools.toMap(),
            categories = categories,
            totalCount = tools.size,
            metadata = mapOf(
                "lastUpdated" to LocalDateTime.now().toString(),
                "platform" to "unhinged"
            )
        )
    }
    
    fun getToolsByCategory(category: String): List<ToolDefinition> = 
        tools.values.filter { it.category == category }
    
    fun searchTools(query: String): List<ToolDefinition> = 
        tools.values.filter { 
            it.name.contains(query, ignoreCase = true) || 
            it.description.contains(query, ignoreCase = true) ||
            it.metadata.tags.any { tag -> tag.contains(query, ignoreCase = true) }
        }
    
    // Tool execution
    suspend fun executeTool(request: ToolExecutionRequest): ToolExecutionResult {
        val startTime = System.currentTimeMillis()
        
        return try {
            val tool = tools[request.toolId]
                ?: return ToolExecutionResult(
                    requestId = request.requestId,
                    toolId = request.toolId,
                    success = false,
                    error = "Tool not found: ${request.toolId}",
                    executionTime = System.currentTimeMillis() - startTime
                )
            
            val result = when (tool.type) {
                ToolType.PLATFORM -> executePlatformTool(tool, request)
                ToolType.LOCAL -> executeLocalTool(tool, request)
                ToolType.REMOTE -> executeRemoteTool(tool, request)
                ToolType.HYBRID -> executeHybridTool(tool, request)
            }
            
            val executionResult = ToolExecutionResult(
                requestId = request.requestId,
                toolId = request.toolId,
                success = true,
                result = result,
                executionTime = System.currentTimeMillis() - startTime
            )
            
            // Store execution history
            executionHistory[request.requestId] = executionResult
            
            executionResult
            
        } catch (e: Exception) {
            ToolExecutionResult(
                requestId = request.requestId,
                toolId = request.toolId,
                success = false,
                error = "Execution failed: ${e.message}",
                executionTime = System.currentTimeMillis() - startTime
            )
        }
    }
    
    private suspend fun executePlatformTool(tool: ToolDefinition, request: ToolExecutionRequest): String {
        return when (tool.id) {
            "llm-query" -> {
                val prompt = request.parameters["prompt"] ?: throw IllegalArgumentException("Missing prompt parameter")
                LlmService.queryLlmStream(prompt)
            }
            "text-to-speech" -> {
                // TTS execution would be handled by TtsService
                "TTS execution not implemented in this context"
            }
            else -> throw IllegalArgumentException("Unknown platform tool: ${tool.id}")
        }
    }
    
    private suspend fun executeLocalTool(tool: ToolDefinition, request: ToolExecutionRequest): String {
        // For local tools, we would typically delegate to the e-cli
        return "Local tool execution not implemented - should be handled by e-cli"
    }
    
    private suspend fun executeRemoteTool(tool: ToolDefinition, request: ToolExecutionRequest): String {
        // For remote tools, make HTTP calls to external services
        tool.endpoint?.let { endpoint ->
            val response = client.post(endpoint) {
                contentType(ContentType.Application.Json)
                setBody(request.parameters)
            }
            return response.body()
        } ?: throw IllegalArgumentException("Remote tool missing endpoint")
    }
    
    private suspend fun executeHybridTool(tool: ToolDefinition, request: ToolExecutionRequest): String {
        // Hybrid tools combine local and platform capabilities
        return "Hybrid tool execution not implemented"
    }
    
    // Execution history
    fun getExecutionHistory(limit: Int = 100): List<ToolExecutionResult> = 
        executionHistory.values.sortedByDescending { it.timestamp }.take(limit)
    
    fun getExecutionResult(requestId: String): ToolExecutionResult? = 
        executionHistory[requestId]
}
