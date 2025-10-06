// ============================================================================
// Multimodal HTTP Controller - Presentation Layer
// ============================================================================
//
// @file MultimodalController.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description HTTP REST endpoints for multimodal AI processing operations
//
// This controller provides HTTP REST endpoints for advanced multimodal image
// analysis functionality. It follows clean architecture by delegating to
// application services and use cases.
//
// ============================================================================

package com.unhinged.presentation.http

import com.unhinged.application.multimodal.MultimodalService
import com.unhinged.domain.multimodal.*
import io.ktor.http.*
import io.ktor.http.content.*
import io.ktor.server.application.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.*
import java.util.*

// ============================================================================
// DTOs for HTTP API
// ============================================================================

@Serializable
data class MultimodalAnalysisResponse(
    val id: String,
    val imageId: String,
    val analysisType: String,
    val description: String,
    val confidence: Double,
    val modelUsed: String,
    val workflowType: String,
    val processingTime: Double,
    val metadata: Map<String, String>,
    val extractedText: String? = null,
    val uiElements: List<UIElementDto> = emptyList(),
    val tags: List<String> = emptyList(),
    val createdAt: String,
    val userId: String? = null
)

@Serializable
data class UIElementDto(
    val type: String,
    val confidence: Double,
    val bounds: ElementBoundsDto? = null,
    val properties: Map<String, String> = emptyMap()
)

@Serializable
data class ElementBoundsDto(
    val x: Int,
    val y: Int,
    val width: Int,
    val height: Int
)

@Serializable
data class AnalysisRequestDto(
    val analysisType: String? = null,
    val workflowType: String? = null,
    val prompt: String? = null,
    val priority: String? = null,
    val maxTokens: Int? = null,
    val temperature: Float? = null,
    val contextHints: Map<String, String> = emptyMap()
)

@Serializable
data class WorkflowConfigurationResponse(
    val type: String,
    val visionModel: String,
    val useContextEnhancement: Boolean,
    val maxIterations: Int,
    val requireConsensus: Boolean,
    val timeoutSeconds: Int,
    val parameters: Map<String, String>
)

@Serializable
data class AnalysisStatisticsResponse(
    val totalAnalyses: Long,
    val averageConfidence: Double,
    val averageProcessingTime: Double,
    val analysisTypeBreakdown: Map<String, Long>,
    val workflowTypeBreakdown: Map<String, Long>,
    val modelUsageBreakdown: Map<String, Long>,
    val dailyAnalysisCount: Map<String, Long>
)

@Serializable
data class ContextItemResponse(
    val id: String,
    val type: String,
    val title: String,
    val content: String,
    val filePath: String,
    val tags: List<String>,
    val relevanceScore: Double,
    val lastModified: String
)

@Serializable
data class ErrorResponse(
    val error: String,
    val code: String? = null,
    val details: Map<String, String> = emptyMap()
)

// ============================================================================
// HTTP Controller
// ============================================================================

/**
 * HTTP REST controller for multimodal AI operations
 * 
 * Provides endpoints for advanced image analysis with multiple workflows,
 * context enhancement, and comprehensive result management.
 */
class MultimodalController(
    private val multimodalService: MultimodalService
) {
    
    fun Route.multimodalRoutes() {
        route("/api/multimodal") {
            
            // Main analysis endpoint
            post("/analyze") {
                try {
                    val multipart = call.receiveMultipart()
                    var imageData: ByteArray? = null
                    var requestDto = AnalysisRequestDto()
                    
                    multipart.forEachPart { part ->
                        when (part) {
                            is PartData.FileItem -> {
                                if (part.name == "image") {
                                    imageData = part.streamProvider().readBytes()
                                }
                            }
                            is PartData.FormItem -> {
                                when (part.name) {
                                    "analysisType" -> requestDto = requestDto.copy(analysisType = part.value)
                                    "workflowType" -> requestDto = requestDto.copy(workflowType = part.value)
                                    "prompt" -> requestDto = requestDto.copy(prompt = part.value)
                                    "priority" -> requestDto = requestDto.copy(priority = part.value)
                                    "maxTokens" -> requestDto = requestDto.copy(maxTokens = part.value.toIntOrNull())
                                    "temperature" -> requestDto = requestDto.copy(temperature = part.value.toFloatOrNull())
                                }
                            }
                        }
                        part.dispose()
                    }
                    
                    if (imageData == null) {
                        call.respond(HttpStatusCode.BadRequest, ErrorResponse("No image provided"))
                        return@post
                    }
                    
                    // Create analysis request
                    val analysisRequest = AnalysisRequest(
                        imageId = UUID.randomUUID().toString(),
                        imageData = imageData!!,
                        analysisType = requestDto.analysisType?.let { 
                            AnalysisType.valueOf(it.uppercase()) 
                        } ?: AnalysisType.SCREENSHOT,
                        workflowType = requestDto.workflowType?.let { 
                            WorkflowType.valueOf(it.uppercase()) 
                        },
                        prompt = requestDto.prompt,
                        priority = requestDto.priority?.let { 
                            Priority.valueOf(it.uppercase()) 
                        } ?: Priority.NORMAL,
                        userId = call.request.headers["X-User-ID"], // Get from auth header
                        maxTokens = requestDto.maxTokens ?: 1024,
                        temperature = requestDto.temperature ?: 0.1f,
                        contextHints = requestDto.contextHints.mapValues { it.value as Any }
                    )
                    
                    // Execute analysis
                    val result = multimodalService.analyzeImage(analysisRequest)
                    
                    // Convert to response DTO
                    val response = MultimodalAnalysisResponse(
                        id = result.id,
                        imageId = result.imageId,
                        analysisType = result.analysisType.name.lowercase(),
                        description = result.description,
                        confidence = result.confidence,
                        modelUsed = result.modelUsed,
                        workflowType = result.workflowType.name.lowercase(),
                        processingTime = result.processingTime,
                        metadata = result.metadata,
                        extractedText = result.extractedText,
                        uiElements = result.uiElements.map { element ->
                            UIElementDto(
                                type = element.type,
                                confidence = element.confidence,
                                bounds = element.bounds?.let { bounds ->
                                    ElementBoundsDto(bounds.x, bounds.y, bounds.width, bounds.height)
                                },
                                properties = element.properties
                            )
                        },
                        tags = result.tags,
                        createdAt = result.createdAt.toString(),
                        userId = result.userId
                    )
                    
                    call.respond(HttpStatusCode.OK, response)
                    
                } catch (e: MultimodalValidationException) {
                    call.respond(HttpStatusCode.BadRequest, ErrorResponse(
                        error = e.message ?: "Validation failed",
                        code = "VALIDATION_ERROR",
                        details = e.errors.associate { it.field to it.message }
                    ))
                } catch (e: MultimodalProcessingException) {
                    call.respond(HttpStatusCode.InternalServerError, ErrorResponse(
                        error = e.message ?: "Processing failed",
                        code = "PROCESSING_ERROR"
                    ))
                } catch (e: Exception) {
                    call.respond(HttpStatusCode.InternalServerError, ErrorResponse(
                        error = "Internal server error: ${e.message}",
                        code = "INTERNAL_ERROR"
                    ))
                }
            }
            
            // Get analysis by ID
            get("/analysis/{id}") {
                try {
                    val id = call.parameters["id"] ?: run {
                        call.respond(HttpStatusCode.BadRequest, ErrorResponse("Missing analysis ID"))
                        return@get
                    }
                    
                    val analysis = multimodalService.getAnalysis(id)
                    
                    val response = MultimodalAnalysisResponse(
                        id = analysis.id,
                        imageId = analysis.imageId,
                        analysisType = analysis.analysisType.name.lowercase(),
                        description = analysis.description,
                        confidence = analysis.confidence,
                        modelUsed = analysis.modelUsed,
                        workflowType = analysis.workflowType.name.lowercase(),
                        processingTime = analysis.processingTime,
                        metadata = analysis.metadata,
                        extractedText = analysis.extractedText,
                        uiElements = analysis.uiElements.map { element ->
                            UIElementDto(
                                type = element.type,
                                confidence = element.confidence,
                                bounds = element.bounds?.let { bounds ->
                                    ElementBoundsDto(bounds.x, bounds.y, bounds.width, bounds.height)
                                },
                                properties = element.properties
                            )
                        },
                        tags = analysis.tags,
                        createdAt = analysis.createdAt.toString(),
                        userId = analysis.userId
                    )
                    
                    call.respond(HttpStatusCode.OK, response)
                    
                } catch (e: MultimodalNotFoundException) {
                    call.respond(HttpStatusCode.NotFound, ErrorResponse(
                        error = e.message ?: "Analysis not found",
                        code = "NOT_FOUND"
                    ))
                } catch (e: Exception) {
                    call.respond(HttpStatusCode.InternalServerError, ErrorResponse(
                        error = "Internal server error: ${e.message}",
                        code = "INTERNAL_ERROR"
                    ))
                }
            }
            
            // Get user analyses
            get("/analyses") {
                try {
                    val userId = call.request.headers["X-User-ID"] ?: run {
                        call.respond(HttpStatusCode.Unauthorized, ErrorResponse("User ID required"))
                        return@get
                    }
                    
                    val limit = call.request.queryParameters["limit"]?.toIntOrNull() ?: 50
                    val offset = call.request.queryParameters["offset"]?.toIntOrNull() ?: 0
                    
                    val analyses = multimodalService.getUserAnalyses(userId, limit, offset)
                    
                    val responses = analyses.map { analysis ->
                        MultimodalAnalysisResponse(
                            id = analysis.id,
                            imageId = analysis.imageId,
                            analysisType = analysis.analysisType.name.lowercase(),
                            description = analysis.description,
                            confidence = analysis.confidence,
                            modelUsed = analysis.modelUsed,
                            workflowType = analysis.workflowType.name.lowercase(),
                            processingTime = analysis.processingTime,
                            metadata = analysis.metadata,
                            extractedText = analysis.extractedText,
                            uiElements = analysis.uiElements.map { element ->
                                UIElementDto(
                                    type = element.type,
                                    confidence = element.confidence,
                                    bounds = element.bounds?.let { bounds ->
                                        ElementBoundsDto(bounds.x, bounds.y, bounds.width, bounds.height)
                                    },
                                    properties = element.properties
                                )
                            },
                            tags = analysis.tags,
                            createdAt = analysis.createdAt.toString(),
                            userId = analysis.userId
                        )
                    }
                    
                    call.respond(HttpStatusCode.OK, mapOf(
                        "analyses" to responses,
                        "total" to responses.size,
                        "limit" to limit,
                        "offset" to offset
                    ))
                    
                } catch (e: Exception) {
                    call.respond(HttpStatusCode.InternalServerError, ErrorResponse(
                        error = "Internal server error: ${e.message}",
                        code = "INTERNAL_ERROR"
                    ))
                }
            }

            // Get available workflows
            get("/workflows") {
                try {
                    val analysisTypeParam = call.request.queryParameters["analysisType"]

                    if (analysisTypeParam != null) {
                        val analysisType = AnalysisType.valueOf(analysisTypeParam.uppercase())
                        val workflows = multimodalService.getAvailableWorkflows(analysisType)

                        val responses = workflows.map { workflow ->
                            WorkflowConfigurationResponse(
                                type = workflow.type.name.lowercase(),
                                visionModel = workflow.visionModel,
                                useContextEnhancement = workflow.useContextEnhancement,
                                maxIterations = workflow.maxIterations,
                                requireConsensus = workflow.requireConsensus,
                                timeoutSeconds = workflow.timeoutSeconds,
                                parameters = workflow.parameters.mapValues { it.value.toString() }
                            )
                        }

                        call.respond(HttpStatusCode.OK, mapOf(
                            "analysisType" to analysisTypeParam.lowercase(),
                            "workflows" to responses
                        ))
                    } else {
                        // Return all workflow types
                        val allWorkflows = WorkflowType.values().map { workflowType ->
                            mapOf(
                                "type" to workflowType.name.lowercase(),
                                "name" to workflowType.name.replace("_", " ").lowercase()
                                    .split(" ").joinToString(" ") { it.capitalize() },
                                "description" to getWorkflowDescription(workflowType)
                            )
                        }

                        call.respond(HttpStatusCode.OK, mapOf("workflows" to allWorkflows))
                    }

                } catch (e: IllegalArgumentException) {
                    call.respond(HttpStatusCode.BadRequest, ErrorResponse(
                        error = "Invalid analysis type",
                        code = "INVALID_ANALYSIS_TYPE"
                    ))
                } catch (e: Exception) {
                    call.respond(HttpStatusCode.InternalServerError, ErrorResponse(
                        error = "Internal server error: ${e.message}",
                        code = "INTERNAL_ERROR"
                    ))
                }
            }
        }
    }

    /**
     * Get workflow description for display
     */
    private fun getWorkflowDescription(workflow: WorkflowType): String = when (workflow) {
        WorkflowType.BASIC_ANALYSIS -> "Single model analysis with fastest processing"
        WorkflowType.CONTEXTUAL_ANALYSIS -> "Enhanced analysis with project context and documentation"
        WorkflowType.ITERATIVE_REFINEMENT -> "Multi-pass analysis for highest quality and detail"
        WorkflowType.MULTI_MODEL_CONSENSUS -> "Multiple models for validation and consensus"
    }
}
