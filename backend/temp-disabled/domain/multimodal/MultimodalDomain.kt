// ============================================================================
// Multimodal Domain - Core Business Logic
// ============================================================================
//
// @file MultimodalDomain.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Core multimodal domain entities and business logic for advanced image analysis
//
// This file implements the domain layer for multimodal processing, following
// clean architecture principles. All entities and business rules are
// independent of infrastructure concerns.
//
// ============================================================================

package com.unhinged.domain.multimodal

import java.time.Instant
import java.util.*

// ============================================================================
// Core Multimodal Entities
// ============================================================================

/**
 * Comprehensive multimodal analysis result with enhanced AI capabilities
 */
data class MultimodalAnalysis(
    val id: String = UUID.randomUUID().toString(),
    val imageId: String,
    val analysisType: AnalysisType,
    val description: String,
    val confidence: Double,
    val modelUsed: String,
    val workflowType: WorkflowType,
    val processingTime: Double,
    val metadata: Map<String, String> = emptyMap(),
    val extractedText: String? = null,
    val uiElements: List<UIElement> = emptyList(),
    val tags: List<String> = emptyList(),
    val createdAt: Instant = Instant.now(),
    val userId: String? = null,
    val sessionId: String? = null
) {
    init {
        require(imageId.isNotBlank()) { "Image ID cannot be blank" }
        require(description.isNotBlank()) { "Description cannot be blank" }
        require(confidence in 0.0..1.0) { "Confidence must be between 0.0 and 1.0" }
        require(modelUsed.isNotBlank()) { "Model used cannot be blank" }
        require(processingTime >= 0.0) { "Processing time must be non-negative" }
    }
}

/**
 * UI element detected in image analysis
 */
data class UIElement(
    val type: String,
    val confidence: Double,
    val bounds: ElementBounds? = null,
    val properties: Map<String, String> = emptyMap()
) {
    init {
        require(type.isNotBlank()) { "UI element type cannot be blank" }
        require(confidence in 0.0..1.0) { "Confidence must be between 0.0 and 1.0" }
    }
}

/**
 * Bounding box coordinates for UI elements
 */
data class ElementBounds(
    val x: Int,
    val y: Int,
    val width: Int,
    val height: Int
) {
    init {
        require(x >= 0) { "X coordinate must be non-negative" }
        require(y >= 0) { "Y coordinate must be non-negative" }
        require(width > 0) { "Width must be positive" }
        require(height > 0) { "Height must be positive" }
    }
}

/**
 * Analysis request containing all parameters for multimodal processing
 */
data class AnalysisRequest(
    val imageId: String,
    val imageData: ByteArray,
    val analysisType: AnalysisType,
    val workflowType: WorkflowType? = null,
    val prompt: String? = null,
    val priority: Priority = Priority.NORMAL,
    val userId: String? = null,
    val contextHints: Map<String, Any> = emptyMap(),
    val maxTokens: Int = 1024,
    val temperature: Float = 0.1f
) {
    init {
        require(imageId.isNotBlank()) { "Image ID cannot be blank" }
        require(imageData.isNotEmpty()) { "Image data cannot be empty" }
        require(maxTokens > 0) { "Max tokens must be positive" }
        require(temperature in 0.0f..2.0f) { "Temperature must be between 0.0 and 2.0" }
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (javaClass != other?.javaClass) return false

        other as AnalysisRequest

        if (imageId != other.imageId) return false
        if (!imageData.contentEquals(other.imageData)) return false
        if (analysisType != other.analysisType) return false
        if (workflowType != other.workflowType) return false
        if (prompt != other.prompt) return false
        if (priority != other.priority) return false
        if (userId != other.userId) return false
        if (contextHints != other.contextHints) return false
        if (maxTokens != other.maxTokens) return false
        if (temperature != other.temperature) return false

        return true
    }

    override fun hashCode(): Int {
        var result = imageId.hashCode()
        result = 31 * result + imageData.contentHashCode()
        result = 31 * result + analysisType.hashCode()
        result = 31 * result + (workflowType?.hashCode() ?: 0)
        result = 31 * result + (prompt?.hashCode() ?: 0)
        result = 31 * result + priority.hashCode()
        result = 31 * result + (userId?.hashCode() ?: 0)
        result = 31 * result + contextHints.hashCode()
        result = 31 * result + maxTokens
        result = 31 * result + temperature.hashCode()
        return result
    }
}

/**
 * Workflow configuration for analysis execution
 */
data class WorkflowConfiguration(
    val type: WorkflowType,
    val visionModel: String,
    val useContextEnhancement: Boolean,
    val maxIterations: Int,
    val requireConsensus: Boolean,
    val timeoutSeconds: Int,
    val parameters: Map<String, Any> = emptyMap()
) {
    init {
        require(visionModel.isNotBlank()) { "Vision model cannot be blank" }
        require(maxIterations > 0) { "Max iterations must be positive" }
        require(timeoutSeconds > 0) { "Timeout must be positive" }
    }
}

/**
 * Context item from documentation or codebase
 */
data class ContextItem(
    val id: String,
    val type: ContextType,
    val title: String,
    val content: String,
    val filePath: String,
    val tags: List<String> = emptyList(),
    val relevanceScore: Double = 0.0,
    val lastModified: Instant = Instant.now()
) {
    init {
        require(id.isNotBlank()) { "Context item ID cannot be blank" }
        require(title.isNotBlank()) { "Context item title cannot be blank" }
        require(content.isNotBlank()) { "Context item content cannot be blank" }
        require(filePath.isNotBlank()) { "Context item file path cannot be blank" }
        require(relevanceScore in 0.0..1.0) { "Relevance score must be between 0.0 and 1.0" }
    }
}

// ============================================================================
// Enums
// ============================================================================

/**
 * Types of analysis supported by the multimodal system
 */
enum class AnalysisType {
    SCREENSHOT,
    NATURAL_IMAGE,
    DOCUMENT,
    UI_COMPONENT,
    OCR_FOCUSED
}

/**
 * Workflow types for different analysis approaches
 */
enum class WorkflowType {
    BASIC_ANALYSIS,
    CONTEXTUAL_ANALYSIS,
    ITERATIVE_REFINEMENT,
    MULTI_MODEL_CONSENSUS
}

/**
 * Priority levels for analysis requests
 */
enum class Priority {
    LOW,
    NORMAL,
    HIGH,
    CRITICAL
}

/**
 * Types of context available for analysis enhancement
 */
enum class ContextType {
    DOCUMENTATION,
    UI_COMPONENTS,
    API_ENDPOINTS,
    ARCHITECTURE,
    CODEBASE
}

// ============================================================================
// Validation Errors and Exceptions
// ============================================================================

/**
 * Multimodal validation error
 */
data class MultimodalValidationError(
    val field: String,
    val message: String,
    val code: String
)

/**
 * Multimodal processing exception
 */
class MultimodalProcessingException(
    message: String,
    cause: Throwable? = null
) : Exception(message, cause)

/**
 * Multimodal validation exception
 */
class MultimodalValidationException(
    message: String,
    val errors: List<MultimodalValidationError>
) : Exception(message)

/**
 * Multimodal analysis not found exception
 */
class MultimodalNotFoundException(
    message: String
) : Exception(message)

/**
 * Workflow configuration exception
 */
class WorkflowConfigurationException(
    message: String,
    cause: Throwable? = null
) : Exception(message, cause)
