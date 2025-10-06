// ============================================================================
// Vision HTTP Controller - Presentation Layer
// ============================================================================
//
// @file VisionController.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description HTTP REST endpoints for vision processing operations
//
// This controller provides HTTP REST endpoints for image processing
// functionality. It follows clean architecture by delegating to use cases.
//
// ============================================================================

package com.unhinged.presentation.http

import com.unhinged.application.vision.*
import com.unhinged.domain.vision.*
import io.ktor.http.*
import io.ktor.http.content.*
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.*

// ============================================================================
// DTOs for HTTP API
// ============================================================================

@Serializable
data class ImageAnalysisResponse(
    val id: String,
    val description: String,
    val confidence: Float,
    val metadata: ImageMetadataDto,
    val tags: List<String>,
    val objects: List<DetectedObjectDto>,
    val processingTimeMs: Long
)

@Serializable
data class ImageMetadataDto(
    val width: Int,
    val height: Int,
    val format: String,
    val sizeBytes: Long,
    val colorSpace: String
)

@Serializable
data class DetectedObjectDto(
    val label: String,
    val confidence: Float,
    val boundingBox: BoundingBoxDto? = null
)

@Serializable
data class BoundingBoxDto(
    val x: Int,
    val y: Int,
    val width: Int,
    val height: Int
)

@Serializable
data class ImageDescriptionResponse(
    val description: String,
    val promptUsed: String?
)

@Serializable
data class ObjectDetectionResponse(
    val objects: List<DetectedObjectDto>
)

@Serializable
data class ErrorResponse(
    val error: String,
    val details: List<String> = emptyList()
)

// ============================================================================
// Vision Controller
// ============================================================================

/**
 * HTTP controller for vision operations
 * 
 * Provides REST endpoints for image processing functionality.
 */
class VisionController(
    private val imageAnalysisUseCase: ImageAnalysisUseCase,
    private val imageDescriptionUseCase: ImageDescriptionUseCase,
    private val objectDetectionUseCase: ObjectDetectionUseCase,
    private val visionHealthCheckUseCase: VisionHealthCheckUseCase
) {
    
    fun configureRoutes(routing: Routing) {
        routing.route("/api/v1/vision") {
            
            // Image analysis endpoint
            post("/analyze") {
                try {
                    val userId = call.request.headers["X-User-ID"] ?: "anonymous"
                    
                    // Get image data from multipart request
                    val multipart = call.receiveMultipart()
                    var imageData: ByteArray? = null
                    var generateTags = true
                    var detectObjects = false
                    var maxDescriptionLength = 100
                    var language = "en"
                    
                    multipart.forEachPart { part ->
                        when (part) {
                            is PartData.FileItem -> {
                                if (part.name == "image") {
                                    imageData = part.streamProvider().readBytes()
                                }
                            }
                            is PartData.FormItem -> {
                                when (part.name) {
                                    "generateTags" -> generateTags = part.value.toBoolean()
                                    "detectObjects" -> detectObjects = part.value.toBoolean()
                                    "maxDescriptionLength" -> maxDescriptionLength = part.value.toInt()
                                    "language" -> language = part.value
                                }
                            }
                            else -> {}
                        }
                        part.dispose()
                    }
                    
                    if (imageData == null) {
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse("No image file provided")
                        )
                        return@post
                    }
                    
                    // Create processing options
                    val options = VisionOptions(
                        generateTags = generateTags,
                        detectObjects = detectObjects,
                        maxDescriptionLength = maxDescriptionLength,
                        language = language
                    )
                    
                    // Execute use case
                    val analysis = imageAnalysisUseCase.execute(imageData!!, userId, options)
                    
                    call.respond(
                        HttpStatusCode.OK,
                        ImageAnalysisResponse(
                            id = analysis.id,
                            description = analysis.description,
                            confidence = analysis.confidence,
                            metadata = analysis.metadata.toDto(),
                            tags = analysis.tags,
                            objects = analysis.objects.map { it.toDto() },
                            processingTimeMs = analysis.processingTimeMs
                        )
                    )
                    
                } catch (e: VisionValidationException) {
                    call.respond(
                        HttpStatusCode.BadRequest,
                        ErrorResponse("Validation failed", e.errors.map { it.message })
                    )
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.InternalServerError,
                        ErrorResponse("Image analysis failed", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
            
            // Image description endpoint
            post("/describe") {
                try {
                    val userId = call.request.headers["X-User-ID"] ?: "anonymous"
                    
                    // Get image data from multipart request
                    val multipart = call.receiveMultipart()
                    var imageData: ByteArray? = null
                    var prompt: String? = null
                    var maxDescriptionLength = 100
                    var language = "en"
                    
                    multipart.forEachPart { part ->
                        when (part) {
                            is PartData.FileItem -> {
                                if (part.name == "image") {
                                    imageData = part.streamProvider().readBytes()
                                }
                            }
                            is PartData.FormItem -> {
                                when (part.name) {
                                    "prompt" -> prompt = part.value
                                    "maxDescriptionLength" -> maxDescriptionLength = part.value.toInt()
                                    "language" -> language = part.value
                                }
                            }
                            else -> {}
                        }
                        part.dispose()
                    }
                    
                    if (imageData == null) {
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse("No image file provided")
                        )
                        return@post
                    }
                    
                    // Create processing options
                    val options = VisionOptions(
                        maxDescriptionLength = maxDescriptionLength,
                        language = language,
                        prompt = prompt
                    )
                    
                    // Execute use case
                    val description = imageDescriptionUseCase.execute(imageData!!, prompt, userId, options)
                    
                    call.respond(
                        HttpStatusCode.OK,
                        ImageDescriptionResponse(
                            description = description,
                            promptUsed = prompt
                        )
                    )
                    
                } catch (e: VisionValidationException) {
                    call.respond(
                        HttpStatusCode.BadRequest,
                        ErrorResponse("Validation failed", e.errors.map { it.message })
                    )
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.InternalServerError,
                        ErrorResponse("Image description failed", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
            
            // Object detection endpoint
            post("/detect") {
                try {
                    val userId = call.request.headers["X-User-ID"] ?: "anonymous"
                    
                    // Get image data from multipart request
                    val multipart = call.receiveMultipart()
                    var imageData: ByteArray? = null
                    
                    multipart.forEachPart { part ->
                        when (part) {
                            is PartData.FileItem -> {
                                if (part.name == "image") {
                                    imageData = part.streamProvider().readBytes()
                                }
                            }
                            else -> {}
                        }
                        part.dispose()
                    }
                    
                    if (imageData == null) {
                        call.respond(
                            HttpStatusCode.BadRequest,
                            ErrorResponse("No image file provided")
                        )
                        return@post
                    }
                    
                    // Execute use case
                    val objects = objectDetectionUseCase.execute(imageData!!, userId)
                    
                    call.respond(
                        HttpStatusCode.OK,
                        ObjectDetectionResponse(
                            objects = objects.map { it.toDto() }
                        )
                    )
                    
                } catch (e: VisionValidationException) {
                    call.respond(
                        HttpStatusCode.BadRequest,
                        ErrorResponse("Validation failed", e.errors.map { it.message })
                    )
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.InternalServerError,
                        ErrorResponse("Object detection failed", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
            
            // Health check endpoint
            get("/health") {
                try {
                    val health = visionHealthCheckUseCase.execute()
                    call.respond(
                        HttpStatusCode.OK,
                        mapOf(
                            "status" to if (health.isHealthy) "healthy" else "unhealthy",
                            "visionModelLoaded" to health.visionModelLoaded,
                            "cudaAvailable" to health.cudaAvailable,
                            "service" to "vision-processing",
                            "version" to health.version,
                            "capabilities" to health.capabilities
                        )
                    )
                } catch (e: Exception) {
                    call.respond(
                        HttpStatusCode.ServiceUnavailable,
                        ErrorResponse("Vision service unhealthy", listOf(e.message ?: "Unknown error"))
                    )
                }
            }
        }
    }
}

// ============================================================================
// Extension Functions for DTO Conversion
// ============================================================================

private fun ImageMetadata.toDto() = ImageMetadataDto(
    width = width,
    height = height,
    format = format.name,
    sizeBytes = sizeBytes,
    colorSpace = colorSpace
)

private fun DetectedObject.toDto() = DetectedObjectDto(
    label = label,
    confidence = confidence,
    boundingBox = boundingBox?.toDto()
)

private fun BoundingBox.toDto() = BoundingBoxDto(
    x = x,
    y = y,
    width = width,
    height = height
)
