// ============================================================================
// Vision Use Cases - Application Layer
// ============================================================================
//
// @file VisionUseCases.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Application layer use cases for vision processing operations
//
// This layer orchestrates domain objects and coordinates with infrastructure.
// It implements the business workflows for image processing while
// maintaining clean architecture principles.
//
// ============================================================================

package com.unhinged.application.vision

import com.unhinged.domain.vision.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

// ============================================================================
// Use Case Interfaces
// ============================================================================

/**
 * Image analysis use case
 * 
 * Handles the complete workflow for analyzing uploaded images
 */
class ImageAnalysisUseCase(
    private val visionProcessingService: VisionProcessingService,
    private val visionRepository: VisionRepository,
    private val sessionRepository: VisionSessionRepository,
    private val domainService: VisionDomainService
) {
    
    /**
     * Executes image analysis workflow
     * 
     * @param imageData The image data to analyze
     * @param userId The requesting user ID
     * @param options Processing options
     * @return Analysis result
     */
    suspend fun execute(
        imageData: ByteArray,
        userId: String,
        options: VisionOptions = VisionOptions()
    ): ImageAnalysis {
        
        // Validate the request
        val validationErrors = domainService.validateImageAnalysisRequest(imageData, options)
        if (validationErrors.isNotEmpty()) {
            throw VisionValidationException("Invalid image analysis request", validationErrors)
        }
        
        // Create session for tracking
        val session = VisionSession(
            userId = userId,
            sessionType = VisionSessionType.IMAGE_ANALYSIS,
            metadata = domainService.generateSessionMetadata(
                VisionSessionType.IMAGE_ANALYSIS,
                userId,
                mapOf(
                    "image_size" to imageData.size.toString(),
                    "generate_tags" to options.generateTags.toString(),
                    "detect_objects" to options.detectObjects.toString()
                )
            )
        )
        
        val createdSession = sessionRepository.createSession(session)
        
        return try {
            // Process with infrastructure service
            val analysis = visionProcessingService.analyzeImage(imageData, options)
            
            // Validate the result
            val resultValidationErrors = domainService.validateImageAnalysis(analysis)
            if (resultValidationErrors.isNotEmpty()) {
                throw VisionValidationException("Invalid analysis result", resultValidationErrors)
            }
            
            // Save analysis
            val savedAnalysis = visionRepository.saveImageAnalysis(analysis)
            
            // Update session status
            sessionRepository.updateSessionStatus(createdSession.id, VisionSessionStatus.COMPLETED)
            
            savedAnalysis
            
        } catch (e: Exception) {
            sessionRepository.updateSessionStatus(createdSession.id, VisionSessionStatus.FAILED)
            throw VisionProcessingException("Image analysis failed", e)
        }
    }
}

/**
 * Image description use case
 * 
 * Handles generating detailed descriptions of images
 */
class ImageDescriptionUseCase(
    private val visionProcessingService: VisionProcessingService,
    private val sessionRepository: VisionSessionRepository,
    private val domainService: VisionDomainService
) {
    
    /**
     * Executes image description workflow
     * 
     * @param imageData The image data to describe
     * @param prompt Optional prompt for guided description
     * @param userId The requesting user ID
     * @param options Processing options
     * @return Description text
     */
    suspend fun execute(
        imageData: ByteArray,
        prompt: String? = null,
        userId: String,
        options: VisionOptions = VisionOptions()
    ): String {
        
        // Validate the request
        val validationErrors = domainService.validateImageAnalysisRequest(imageData, options)
        if (validationErrors.isNotEmpty()) {
            throw VisionValidationException("Invalid image description request", validationErrors)
        }
        
        // Create session for tracking
        val session = VisionSession(
            userId = userId,
            sessionType = VisionSessionType.IMAGE_DESCRIPTION,
            metadata = domainService.generateSessionMetadata(
                VisionSessionType.IMAGE_DESCRIPTION,
                userId,
                mapOf(
                    "image_size" to imageData.size.toString(),
                    "has_prompt" to (prompt != null).toString(),
                    "max_length" to options.maxDescriptionLength.toString()
                )
            )
        )
        
        val createdSession = sessionRepository.createSession(session)
        
        return try {
            // Process with infrastructure service
            val description = visionProcessingService.describeImage(imageData, prompt, options)
            
            // Update session status
            sessionRepository.updateSessionStatus(createdSession.id, VisionSessionStatus.COMPLETED)
            
            description
            
        } catch (e: Exception) {
            sessionRepository.updateSessionStatus(createdSession.id, VisionSessionStatus.FAILED)
            throw VisionProcessingException("Image description failed", e)
        }
    }
}

/**
 * Object detection use case
 * 
 * Handles detecting and identifying objects in images
 */
class ObjectDetectionUseCase(
    private val visionProcessingService: VisionProcessingService,
    private val sessionRepository: VisionSessionRepository,
    private val domainService: VisionDomainService
) {
    
    /**
     * Executes object detection workflow
     * 
     * @param imageData The image data to analyze
     * @param userId The requesting user ID
     * @param options Processing options
     * @return List of detected objects
     */
    suspend fun execute(
        imageData: ByteArray,
        userId: String,
        options: VisionOptions = VisionOptions()
    ): List<DetectedObject> {
        
        // Validate the request
        val validationErrors = domainService.validateImageAnalysisRequest(imageData, options)
        if (validationErrors.isNotEmpty()) {
            throw VisionValidationException("Invalid object detection request", validationErrors)
        }
        
        // Create session for tracking
        val session = VisionSession(
            userId = userId,
            sessionType = VisionSessionType.OBJECT_DETECTION,
            metadata = domainService.generateSessionMetadata(
                VisionSessionType.OBJECT_DETECTION,
                userId,
                mapOf("image_size" to imageData.size.toString())
            )
        )
        
        val createdSession = sessionRepository.createSession(session)
        
        return try {
            // Process with infrastructure service
            val objects = visionProcessingService.detectObjects(imageData, options)
            
            // Update session status
            sessionRepository.updateSessionStatus(createdSession.id, VisionSessionStatus.COMPLETED)
            
            objects
            
        } catch (e: Exception) {
            sessionRepository.updateSessionStatus(createdSession.id, VisionSessionStatus.FAILED)
            throw VisionProcessingException("Object detection failed", e)
        }
    }
}

/**
 * Vision service health check use case
 */
class VisionHealthCheckUseCase(
    private val visionProcessingService: VisionProcessingService
) {
    
    /**
     * Checks the health of the vision processing service
     * 
     * @return Service health status
     */
    suspend fun execute(): VisionServiceHealth {
        return visionProcessingService.checkHealth()
    }
}
