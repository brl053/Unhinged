// ============================================================================
// Vision Domain - Core Business Logic
// ============================================================================
//
// @file VisionDomain.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Core vision domain entities and business logic for image processing
//
// This file implements the domain layer for vision processing, following
// clean architecture principles. All entities and business rules are
// independent of infrastructure concerns.
//
// ============================================================================

package com.unhinged.domain.vision

import java.time.Instant
import java.util.*

// ============================================================================
// Core Vision Entities
// ============================================================================

/**
 * Image analysis result containing AI-generated description and metadata
 */
data class ImageAnalysis(
    val id: String = UUID.randomUUID().toString(),
    val imageId: String,
    val description: String,
    val confidence: Float,
    val metadata: ImageMetadata,
    val tags: List<String> = emptyList(),
    val objects: List<DetectedObject> = emptyList(),
    val createdAt: Instant = Instant.now(),
    val processingTimeMs: Long = 0
) {
    init {
        require(imageId.isNotBlank()) { "Image ID cannot be blank" }
        require(description.isNotBlank()) { "Description cannot be blank" }
        require(confidence in 0.0f..1.0f) { "Confidence must be between 0.0 and 1.0" }
    }
}

/**
 * Image metadata containing technical information
 */
data class ImageMetadata(
    val width: Int,
    val height: Int,
    val format: ImageFormat,
    val sizeBytes: Long,
    val colorSpace: String = "RGB",
    val hasAlpha: Boolean = false,
    val dpi: Int? = null
) {
    init {
        require(width > 0) { "Width must be positive" }
        require(height > 0) { "Height must be positive" }
        require(sizeBytes > 0) { "Size must be positive" }
    }
}

/**
 * Detected object within an image
 */
data class DetectedObject(
    val label: String,
    val confidence: Float,
    val boundingBox: BoundingBox? = null
) {
    init {
        require(label.isNotBlank()) { "Label cannot be blank" }
        require(confidence in 0.0f..1.0f) { "Confidence must be between 0.0 and 1.0" }
    }
}

/**
 * Bounding box coordinates for detected objects
 */
data class BoundingBox(
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
 * Vision processing session for tracking operations
 */
data class VisionSession(
    val id: String = UUID.randomUUID().toString(),
    val userId: String,
    val sessionType: VisionSessionType,
    val status: VisionSessionStatus = VisionSessionStatus.ACTIVE,
    val metadata: Map<String, String> = emptyMap(),
    val createdAt: Instant = Instant.now(),
    val updatedAt: Instant = Instant.now()
) {
    init {
        require(userId.isNotBlank()) { "User ID cannot be blank" }
    }
}

/**
 * Vision processing options
 */
data class VisionOptions(
    val generateTags: Boolean = true,
    val detectObjects: Boolean = false,
    val maxDescriptionLength: Int = 100,
    val language: String = "en",
    val prompt: String? = null
) {
    init {
        require(maxDescriptionLength > 0) { "Max description length must be positive" }
        require(language.isNotBlank()) { "Language cannot be blank" }
    }
}

// ============================================================================
// Enums
// ============================================================================

/**
 * Supported image formats
 */
enum class ImageFormat {
    UNSPECIFIED,
    JPEG,
    PNG,
    GIF,
    BMP,
    WEBP,
    TIFF,
    SVG
}

/**
 * Vision session types
 */
enum class VisionSessionType {
    IMAGE_ANALYSIS,
    IMAGE_DESCRIPTION,
    OBJECT_DETECTION,
    IMAGE_CLASSIFICATION
}

/**
 * Vision session status
 */
enum class VisionSessionStatus {
    ACTIVE,
    COMPLETED,
    FAILED,
    CANCELLED
}

/**
 * Vision processing types
 */
enum class VisionProcessingType {
    ANALYZE,
    DESCRIBE,
    DETECT_OBJECTS,
    CLASSIFY,
    EXTRACT_TEXT
}

// ============================================================================
// Validation Errors
// ============================================================================

/**
 * Vision validation error
 */
data class VisionValidationError(
    val field: String,
    val message: String,
    val code: String
)

/**
 * Vision processing exception
 */
class VisionProcessingException(
    message: String,
    cause: Throwable? = null
) : Exception(message, cause)

/**
 * Vision validation exception
 */
class VisionValidationException(
    message: String,
    val errors: List<VisionValidationError>
) : Exception(message)

/**
 * Vision not found exception
 */
class VisionNotFoundException(
    message: String
) : Exception(message)
