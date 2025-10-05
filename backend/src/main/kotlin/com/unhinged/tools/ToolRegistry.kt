package com.unhinged.tools

import kotlinx.serialization.*
import kotlinx.serialization.json.*
import kotlinx.coroutines.*
import java.util.concurrent.ConcurrentHashMap
import java.time.LocalDateTime
import java.util.UUID

/**
 * E-Tools Registry - Dynamic tool discovery and management system
 * Allows any LLM to discover, use, and create tools at runtime
 * Similar to React hooks pattern for tool composition
 */

@Serializable
data class ToolDefinition(
    val id: String = UUID.randomUUID().toString(),
    val name: String,
    val description: String,
    val category: String,
    val version: String = "1.0.0",
    val parameters: List<ToolParameter>,
    val returnType: ToolReturnType,
    val executionType: ToolExecutionType,
    val metadata: ToolMetadata = ToolMetadata(),
    val createdAt: String = LocalDateTime.now().toString(),
    val updatedAt: String = LocalDateTime.now().toString()
)

@Serializable
data class ToolParameter(
    val name: String,
    val type: ParameterType,
    val description: String,
    val required: Boolean = true,
    val defaultValue: String? = null,
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
enum class ParameterType {
    STRING, INTEGER, DOUBLE, BOOLEAN, ARRAY, OBJECT, FILE_PATH, URL, JSON
}

@Serializable
enum class ToolReturnType {
    STRING, JSON, BINARY, STREAM, VOID
}

@Serializable
enum class ToolExecutionType {
    SYNCHRONOUS, ASYNCHRONOUS, STREAMING, BATCH
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
    val parameters: Map<String, Any>,
    val context: ExecutionContext = ExecutionContext(),
    val requestId: String = UUID.randomUUID().toString()
)

@Serializable
data class ExecutionContext(
    val userId: String? = null,
    val sessionId: String? = null,
    val llmModel: String? = null,
    val environment: String = "production",
    val timeout: Long = 30000, // 30 seconds default
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

/**
 * Core Tool Registry - Thread-safe registry for managing tools
 */
object ToolRegistry {
    private val tools = ConcurrentHashMap<String, ToolDefinition>()
    private val toolExecutors = ConcurrentHashMap<String, ToolExecutor>()
    private val executionHistory = ConcurrentHashMap<String, ToolExecutionResult>()
    
    // Tool discovery and registration
    fun registerTool(definition: ToolDefinition, executor: ToolExecutor): Boolean {
        return try {
            tools[definition.id] = definition
            toolExecutors[definition.id] = executor
            println("[E-TOOLS] Registered tool: ${definition.name} (${definition.id})")
            true
        } catch (e: Exception) {
            println("[E-TOOLS] Failed to register tool ${definition.name}: ${e.message}")
            false
        }
    }
    
    fun unregisterTool(toolId: String): Boolean {
        return try {
            tools.remove(toolId)
            toolExecutors.remove(toolId)
            println("[E-TOOLS] Unregistered tool: $toolId")
            true
        } catch (e: Exception) {
            println("[E-TOOLS] Failed to unregister tool $toolId: ${e.message}")
            false
        }
    }
    
    fun getTool(toolId: String): ToolDefinition? = tools[toolId]
    
    fun getAllTools(): List<ToolDefinition> = tools.values.toList()
    
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
            
            val executor = toolExecutors[request.toolId]
                ?: return ToolExecutionResult(
                    requestId = request.requestId,
                    toolId = request.toolId,
                    success = false,
                    error = "Executor not found for tool: ${request.toolId}",
                    executionTime = System.currentTimeMillis() - startTime
                )
            
            // Validate parameters
            val validationResult = validateParameters(tool, request.parameters)
            if (!validationResult.isValid) {
                return ToolExecutionResult(
                    requestId = request.requestId,
                    toolId = request.toolId,
                    success = false,
                    error = "Parameter validation failed: ${validationResult.errors.joinToString(", ")}",
                    executionTime = System.currentTimeMillis() - startTime
                )
            }
            
            // Execute with timeout
            val result = withTimeout(request.context.timeout) {
                executor.execute(request.parameters, request.context)
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
            
        } catch (e: TimeoutCancellationException) {
            ToolExecutionResult(
                requestId = request.requestId,
                toolId = request.toolId,
                success = false,
                error = "Tool execution timed out after ${request.context.timeout}ms",
                executionTime = System.currentTimeMillis() - startTime
            )
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
    
    // Parameter validation
    private fun validateParameters(tool: ToolDefinition, parameters: Map<String, Any>): ValidationResult {
        val errors = mutableListOf<String>()
        
        // Check required parameters
        tool.parameters.filter { it.required }.forEach { param ->
            if (!parameters.containsKey(param.name)) {
                errors.add("Missing required parameter: ${param.name}")
            }
        }
        
        // Validate parameter types and constraints
        parameters.forEach { (name, value) ->
            val paramDef = tool.parameters.find { it.name == name }
            if (paramDef != null) {
                val validationError = validateParameter(paramDef, value)
                if (validationError != null) {
                    errors.add(validationError)
                }
            }
        }
        
        return ValidationResult(errors.isEmpty(), errors)
    }
    
    private fun validateParameter(param: ToolParameter, value: Any): String? {
        // Type validation
        val typeValid = when (param.type) {
            ParameterType.STRING -> value is String
            ParameterType.INTEGER -> value is Int || value is Long
            ParameterType.DOUBLE -> value is Double || value is Float
            ParameterType.BOOLEAN -> value is Boolean
            ParameterType.ARRAY -> value is List<*>
            ParameterType.OBJECT -> value is Map<*, *>
            ParameterType.FILE_PATH -> value is String && (value as String).isNotBlank()
            ParameterType.URL -> value is String && (value as String).startsWith("http")
            ParameterType.JSON -> value is String || value is Map<*, *>
        }
        
        if (!typeValid) {
            return "Parameter ${param.name} has invalid type. Expected: ${param.type}"
        }
        
        // Additional validation rules
        param.validation?.let { validation ->
            when (value) {
                is String -> {
                    validation.pattern?.let { pattern ->
                        if (!value.matches(Regex(pattern))) {
                            return "Parameter ${param.name} does not match pattern: $pattern"
                        }
                    }
                    validation.minLength?.let { min ->
                        if (value.length < min) {
                            return "Parameter ${param.name} is too short. Minimum length: $min"
                        }
                    }
                    validation.maxLength?.let { max ->
                        if (value.length > max) {
                            return "Parameter ${param.name} is too long. Maximum length: $max"
                        }
                    }
                    validation.allowedValues?.let { allowed ->
                        if (!allowed.contains(value)) {
                            return "Parameter ${param.name} has invalid value. Allowed: ${allowed.joinToString(", ")}"
                        }
                    }
                }
                is Number -> {
                    val numValue = value.toDouble()
                    validation.minValue?.let { min ->
                        if (numValue < min) {
                            return "Parameter ${param.name} is too small. Minimum: $min"
                        }
                    }
                    validation.maxValue?.let { max ->
                        if (numValue > max) {
                            return "Parameter ${param.name} is too large. Maximum: $max"
                        }
                    }
                }
            }
        }
        
        return null
    }
    
    // Execution history
    fun getExecutionHistory(limit: Int = 100): List<ToolExecutionResult> = 
        executionHistory.values.sortedByDescending { it.timestamp }.take(limit)
    
    fun getExecutionResult(requestId: String): ToolExecutionResult? = 
        executionHistory[requestId]
}

data class ValidationResult(val isValid: Boolean, val errors: List<String>)

/**
 * Interface for tool executors
 */
interface ToolExecutor {
    suspend fun execute(parameters: Map<String, Any>, context: ExecutionContext): String
}
