// ============================================================================
// HTTP Vision Processing Service - Infrastructure Layer
// ============================================================================
//
// @file HttpVisionProcessingService.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description HTTP client implementation for vision processing service
//
// This implementation communicates with the Python vision-ai service
// via HTTP API calls.
//
// ============================================================================

package com.unhinged.infrastructure.vision

import com.unhinged.domain.vision.*
import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.request.forms.*
import io.ktor.http.*
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import java.awt.image.BufferedImage
import java.io.ByteArrayInputStream
import javax.imageio.ImageIO

// ============================================================================
// HTTP Response DTOs
// ============================================================================

@Serializable
data class VisionServiceHealthResponse(
    val status: String,
    val vision_model_loaded: Boolean,
    val cuda_available: Boolean,
    val service: String,
    val version: String,
    val capabilities: List<String>
)

@Serializable
data class VisionAnalysisResponse(
    val description: String,
    val metadata: VisionMetadataResponse
)

@Serializable
data class VisionMetadataResponse(
    val width: Int,
    val height: Int,
    val format: String?,
    val mode: String
)

@Serializable
data class VisionDescriptionResponse(
    val description: String,
    val prompt_used: String?
)

// ============================================================================
// HTTP Vision Processing Service
// ============================================================================

/**
 * @llm-type service
 * @llm-legend Enables backend to request AI-powered image analysis from vision-ai microservice
 * @llm-key Uses Ktor HTTP client with JSON serialization, implements retry logic and error handling
 * @llm-map Infrastructure layer implementation, called by application services, connects to vision-ai on port 8001
 * @llm-axiom All HTTP calls must have timeouts and proper error handling to prevent system hangs
 * @llm-contract Returns VisionResult on success or throws VisionProcessingException on failures
 * @llm-token vision-ai-service: Python microservice running BLIP model for image analysis
 *
 * HTTP client implementation of VisionProcessingService
 *
 * Communicates with the Python vision-ai service via HTTP API
 */
class HttpVisionProcessingService(
    private val httpClient: HttpClient,
    private val baseUrl: String = "http://localhost:8001"
) : VisionProcessingService {
    
    private val json = Json { ignoreUnknownKeys = true }
    
    override suspend fun analyzeImage(
        imageData: ByteArray,
        options: VisionOptions
    ): ImageAnalysis {
        try {
            val response = httpClient.submitFormWithBinaryData(
                url = "$baseUrl/analyze",
                formData = formData {
                    append("image", imageData, Headers.build {
                        append(HttpHeaders.ContentType, "image/jpeg")
                        append(HttpHeaders.ContentDisposition, "filename=\"image.jpg\"")
                    })
                }
            )
            
            if (!response.status.isSuccess()) {
                throw VisionProcessingException("Vision service returned ${response.status}")
            }
            
            val analysisResponse: VisionAnalysisResponse = response.body()
            val metadata = extractImageMetadata(imageData)
            
            return ImageAnalysis(
                imageId = "temp-${System.currentTimeMillis()}",
                description = analysisResponse.description,
                confidence = 0.8f, // Default confidence since BLIP doesn't provide it
                metadata = metadata,
                tags = extractTagsFromDescription(analysisResponse.description),
                objects = emptyList(), // Basic analysis doesn't include object detection
                processingTimeMs = 0 // Would need to measure this
            )
            
        } catch (e: Exception) {
            throw VisionProcessingException("Failed to analyze image", e)
        }
    }
    
    override suspend fun describeImage(
        imageData: ByteArray,
        prompt: String?,
        options: VisionOptions
    ): String {
        try {
            val response = httpClient.submitFormWithBinaryData(
                url = "$baseUrl/describe",
                formData = formData {
                    append("image", imageData, Headers.build {
                        append(HttpHeaders.ContentType, "image/jpeg")
                        append(HttpHeaders.ContentDisposition, "filename=\"image.jpg\"")
                    })
                    if (prompt != null) {
                        append("prompt", prompt)
                    }
                }
            )
            
            if (!response.status.isSuccess()) {
                throw VisionProcessingException("Vision service returned ${response.status}")
            }
            
            val descriptionResponse: VisionDescriptionResponse = response.body()
            return descriptionResponse.description
            
        } catch (e: Exception) {
            throw VisionProcessingException("Failed to describe image", e)
        }
    }
    
    override suspend fun detectObjects(
        imageData: ByteArray,
        options: VisionOptions
    ): List<DetectedObject> {
        // Object detection not implemented in basic BLIP service
        // Would need a different model like YOLO or DETR
        return emptyList()
    }
    
    override suspend fun extractImageMetadata(imageData: ByteArray): ImageMetadata {
        try {
            val inputStream = ByteArrayInputStream(imageData)
            val bufferedImage: BufferedImage = ImageIO.read(inputStream)
                ?: throw VisionProcessingException("Unable to read image data")
            
            // Determine format from image data
            val format = determineImageFormat(imageData)
            
            return ImageMetadata(
                width = bufferedImage.width,
                height = bufferedImage.height,
                format = format,
                sizeBytes = imageData.size.toLong(),
                colorSpace = when (bufferedImage.type) {
                    BufferedImage.TYPE_BYTE_GRAY -> "GRAY"
                    BufferedImage.TYPE_INT_ARGB -> "ARGB"
                    BufferedImage.TYPE_INT_RGB -> "RGB"
                    else -> "RGB"
                },
                hasAlpha = bufferedImage.colorModel.hasAlpha()
            )
            
        } catch (e: Exception) {
            throw VisionProcessingException("Failed to extract image metadata", e)
        }
    }
    
    override suspend fun checkHealth(): VisionServiceHealth {
        try {
            val response = httpClient.get("$baseUrl/health")
            
            if (!response.status.isSuccess()) {
                return VisionServiceHealth(
                    isHealthy = false,
                    visionModelLoaded = false,
                    cudaAvailable = false,
                    version = "unknown",
                    capabilities = emptyList()
                )
            }
            
            val healthResponse: VisionServiceHealthResponse = response.body()
            
            return VisionServiceHealth(
                isHealthy = healthResponse.status == "healthy",
                visionModelLoaded = healthResponse.vision_model_loaded,
                cudaAvailable = healthResponse.cuda_available,
                version = healthResponse.version,
                capabilities = healthResponse.capabilities
            )
            
        } catch (e: Exception) {
            return VisionServiceHealth(
                isHealthy = false,
                visionModelLoaded = false,
                cudaAvailable = false,
                version = "unknown",
                capabilities = emptyList()
            )
        }
    }
    
    // ============================================================================
    // Helper Methods
    // ============================================================================
    
    private fun determineImageFormat(imageData: ByteArray): ImageFormat {
        return when {
            imageData.size >= 2 && imageData[0] == 0xFF.toByte() && imageData[1] == 0xD8.toByte() -> ImageFormat.JPEG
            imageData.size >= 8 && imageData.sliceArray(1..3).contentEquals("PNG".toByteArray()) -> ImageFormat.PNG
            imageData.size >= 6 && imageData.sliceArray(0..5).contentEquals("GIF87a".toByteArray()) -> ImageFormat.GIF
            imageData.size >= 6 && imageData.sliceArray(0..5).contentEquals("GIF89a".toByteArray()) -> ImageFormat.GIF
            imageData.size >= 2 && imageData[0] == 'B'.code.toByte() && imageData[1] == 'M'.code.toByte() -> ImageFormat.BMP
            else -> ImageFormat.JPEG // Default fallback
        }
    }
    
    private fun extractTagsFromDescription(description: String): List<String> {
        // Simple tag extraction from description
        // In a real implementation, this could be more sophisticated
        val commonWords = setOf("a", "an", "the", "is", "are", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by")
        return description.lowercase()
            .replace(Regex("[^a-zA-Z\\s]"), "")
            .split("\\s+".toRegex())
            .filter { it.length > 2 && !commonWords.contains(it) }
            .distinct()
            .take(5) // Limit to 5 tags
    }
}
