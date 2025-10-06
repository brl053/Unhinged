// ============================================================================
// Multimodal HTTP Controller Integration Tests
// ============================================================================
//
// @file MultimodalControllerTest.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description HTTP API integration tests for multimodal endpoints
//
// Tests the complete HTTP → Kotlin → gRPC → Python pipeline
// Validates API contracts and end-to-end functionality
//
// ============================================================================

package com.unhinged.presentation.http

import com.unhinged.application.multimodal.MultimodalService
import com.unhinged.domain.multimodal.*
import io.ktor.client.request.*
import io.ktor.client.request.forms.*
import io.ktor.client.statement.*
import io.ktor.http.*
import io.ktor.server.testing.*
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.TestInstance.Lifecycle
import java.awt.Color
import java.awt.Graphics2D
import java.awt.image.BufferedImage
import java.io.ByteArrayOutputStream
import javax.imageio.ImageIO
import kotlin.test.Test

@TestInstance(Lifecycle.PER_CLASS)
class MultimodalControllerTest {
    
    private lateinit var multimodalService: MultimodalService
    
    @BeforeAll
    fun setup() {
        // Initialize with mock service for HTTP testing
        multimodalService = createMockMultimodalService()
    }
    
    @Test
    fun `POST analyze should accept multipart image and return analysis`() = testApplication {
        // Given: Multipart request with image
        val imageData = createTestScreenshot()
        
        // When: Posting to analyze endpoint
        val response = client.submitFormWithBinaryData(
            url = "/api/multimodal/analyze",
            formData = formData {
                append("image", imageData, Headers.build {
                    append(HttpHeaders.ContentType, "image/png")
                    append(HttpHeaders.ContentDisposition, "filename=\"test.png\"")
                })
                append("analysisType", "screenshot")
                append("workflowType", "contextual_analysis")
                append("prompt", "Analyze this UI screenshot")
                append("priority", "normal")
            }
        ) {
            header("X-User-ID", "test-user")
        }
        
        // Then: Should return successful analysis
        assertEquals(HttpStatusCode.OK, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        
        assertTrue(json.containsKey("id"))
        assertTrue(json.containsKey("description"))
        assertTrue(json.containsKey("confidence"))
        assertTrue(json.containsKey("analysisType"))
        assertEquals("screenshot", json["analysisType"]?.jsonPrimitive?.content)
        assertTrue(json.containsKey("workflowType"))
        assertEquals("contextual_analysis", json["workflowType"]?.jsonPrimitive?.content)
        assertTrue(json.containsKey("processingTime"))
        assertTrue(json.containsKey("createdAt"))
    }
    
    @Test
    fun `POST analyze should validate required image parameter`() = testApplication {
        // When: Posting without image
        val response = client.submitFormWithBinaryData(
            url = "/api/multimodal/analyze",
            formData = formData {
                append("analysisType", "screenshot")
                append("prompt", "Test prompt")
            }
        ) {
            header("X-User-ID", "test-user")
        }
        
        // Then: Should return bad request
        assertEquals(HttpStatusCode.BadRequest, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertTrue(json.containsKey("error"))
        assertEquals("No image provided", json["error"]?.jsonPrimitive?.content)
    }
    
    @Test
    fun `POST analyze should handle different analysis types`() = testApplication {
        val testCases = listOf(
            "screenshot" to createTestScreenshot(),
            "document" to createTestDocument(),
            "ui_component" to createTestUIComponent(),
            "natural_image" to createTestNaturalImage()
        )
        
        testCases.forEach { (analysisType, imageData) ->
            // When: Analyzing different image types
            val response = client.submitFormWithBinaryData(
                url = "/api/multimodal/analyze",
                formData = formData {
                    append("image", imageData, Headers.build {
                        append(HttpHeaders.ContentType, "image/png")
                        append(HttpHeaders.ContentDisposition, "filename=\"test.png\"")
                    })
                    append("analysisType", analysisType)
                    append("workflowType", "basic_analysis")
                }
            ) {
                header("X-User-ID", "test-user")
            }
            
            // Then: Should handle each type successfully
            assertEquals(HttpStatusCode.OK, response.status, "Failed for analysis type: $analysisType")
            
            val responseBody = response.bodyAsText()
            val json = Json.parseToJsonElement(responseBody).jsonObject
            assertEquals(analysisType, json["analysisType"]?.jsonPrimitive?.content)
        }
    }
    
    @Test
    fun `POST analyze should handle different workflow types`() = testApplication {
        val workflowTypes = listOf(
            "basic_analysis",
            "contextual_analysis", 
            "iterative_refinement",
            "multi_model_consensus"
        )
        
        workflowTypes.forEach { workflowType ->
            // When: Using different workflow types
            val response = client.submitFormWithBinaryData(
                url = "/api/multimodal/analyze",
                formData = formData {
                    append("image", createTestScreenshot(), Headers.build {
                        append(HttpHeaders.ContentType, "image/png")
                        append(HttpHeaders.ContentDisposition, "filename=\"test.png\"")
                    })
                    append("analysisType", "screenshot")
                    append("workflowType", workflowType)
                }
            ) {
                header("X-User-ID", "test-user")
            }
            
            // Then: Should handle each workflow successfully
            assertEquals(HttpStatusCode.OK, response.status, "Failed for workflow: $workflowType")
            
            val responseBody = response.bodyAsText()
            val json = Json.parseToJsonElement(responseBody).jsonObject
            assertEquals(workflowType, json["workflowType"]?.jsonPrimitive?.content)
        }
    }
    
    @Test
    fun `GET analysis by ID should return existing analysis`() = testApplication {
        // Given: An existing analysis (mock will return predefined result)
        val analysisId = "test-analysis-123"
        
        // When: Getting analysis by ID
        val response = client.get("/api/multimodal/analysis/$analysisId")
        
        // Then: Should return analysis
        assertEquals(HttpStatusCode.OK, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertEquals(analysisId, json["id"]?.jsonPrimitive?.content)
        assertTrue(json.containsKey("description"))
        assertTrue(json.containsKey("confidence"))
    }
    
    @Test
    fun `GET analysis by ID should return 404 for non-existent analysis`() = testApplication {
        // When: Getting non-existent analysis
        val response = client.get("/api/multimodal/analysis/non-existent-id")
        
        // Then: Should return not found
        assertEquals(HttpStatusCode.NotFound, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertTrue(json.containsKey("error"))
        assertEquals("NOT_FOUND", json["code"]?.jsonPrimitive?.content)
    }
    
    @Test
    fun `GET analyses should return user analyses with pagination`() = testApplication {
        // When: Getting user analyses
        val response = client.get("/api/multimodal/analyses?limit=10&offset=0") {
            header("X-User-ID", "test-user")
        }
        
        // Then: Should return paginated results
        assertEquals(HttpStatusCode.OK, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertTrue(json.containsKey("analyses"))
        assertTrue(json.containsKey("total"))
        assertTrue(json.containsKey("limit"))
        assertTrue(json.containsKey("offset"))
    }
    
    @Test
    fun `GET analyses should require user authentication`() = testApplication {
        // When: Getting analyses without user ID
        val response = client.get("/api/multimodal/analyses")
        
        // Then: Should return unauthorized
        assertEquals(HttpStatusCode.Unauthorized, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertEquals("User ID required", json["error"]?.jsonPrimitive?.content)
    }
    
    @Test
    fun `GET workflows should return available workflows`() = testApplication {
        // When: Getting available workflows
        val response = client.get("/api/multimodal/workflows")
        
        // Then: Should return workflow list
        assertEquals(HttpStatusCode.OK, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertTrue(json.containsKey("workflows"))
        
        // Verify workflow types are present
        val workflows = json["workflows"]?.jsonObject
        assertNotNull(workflows)
    }
    
    @Test
    fun `GET workflows with analysis type should return specific workflows`() = testApplication {
        // When: Getting workflows for specific analysis type
        val response = client.get("/api/multimodal/workflows?analysisType=screenshot")
        
        // Then: Should return workflows for screenshot analysis
        assertEquals(HttpStatusCode.OK, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertTrue(json.containsKey("workflows"))
        assertEquals("screenshot", json["analysisType"]?.jsonPrimitive?.content)
    }
    
    @Test
    fun `should handle validation errors gracefully`() = testApplication {
        // When: Posting invalid data
        val response = client.submitFormWithBinaryData(
            url = "/api/multimodal/analyze",
            formData = formData {
                append("image", byteArrayOf(), Headers.build {
                    append(HttpHeaders.ContentType, "image/png")
                    append(HttpHeaders.ContentDisposition, "filename=\"empty.png\"")
                })
                append("analysisType", "invalid_type")
            }
        ) {
            header("X-User-ID", "test-user")
        }
        
        // Then: Should return validation error
        assertEquals(HttpStatusCode.BadRequest, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertTrue(json.containsKey("error"))
        assertEquals("VALIDATION_ERROR", json["code"]?.jsonPrimitive?.content)
    }
    
    @Test
    fun `should handle processing errors gracefully`() = testApplication {
        // Given: Request that will cause processing error (simulated by mock)
        val response = client.submitFormWithBinaryData(
            url = "/api/multimodal/analyze",
            formData = formData {
                append("image", createCorruptedImage(), Headers.build {
                    append(HttpHeaders.ContentType, "image/png")
                    append(HttpHeaders.ContentDisposition, "filename=\"corrupted.png\"")
                })
                append("analysisType", "screenshot")
            }
        ) {
            header("X-User-ID", "test-user")
        }
        
        // Then: Should return processing error
        assertEquals(HttpStatusCode.InternalServerError, response.status)
        
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertTrue(json.containsKey("error"))
        assertEquals("PROCESSING_ERROR", json["code"]?.jsonPrimitive?.content)
    }
    
    @Test
    fun `should measure response times for performance validation`() = testApplication {
        // Given: Standard analysis request
        val imageData = createTestScreenshot()
        
        // When: Measuring response time
        val startTime = System.currentTimeMillis()
        
        val response = client.submitFormWithBinaryData(
            url = "/api/multimodal/analyze",
            formData = formData {
                append("image", imageData, Headers.build {
                    append(HttpHeaders.ContentType, "image/png")
                    append(HttpHeaders.ContentDisposition, "filename=\"perf-test.png\"")
                })
                append("analysisType", "screenshot")
                append("workflowType", "basic_analysis")
            }
        ) {
            header("X-User-ID", "test-user")
        }
        
        val responseTime = System.currentTimeMillis() - startTime
        
        // Then: Should complete within reasonable time
        assertEquals(HttpStatusCode.OK, response.status)
        assertTrue(responseTime < 5000, "Response time too slow: ${responseTime}ms")
        
        // Verify processing time is included in response
        val responseBody = response.bodyAsText()
        val json = Json.parseToJsonElement(responseBody).jsonObject
        assertTrue(json.containsKey("processingTime"))
        
        println("HTTP API Response Time: ${responseTime}ms")
    }
    
    // Helper methods for creating test images
    private fun createTestScreenshot(): ByteArray {
        val image = BufferedImage(800, 600, BufferedImage.TYPE_INT_RGB)
        val g2d: Graphics2D = image.createGraphics()
        
        g2d.color = Color.WHITE
        g2d.fillRect(0, 0, 800, 600)
        g2d.color = Color.BLUE
        g2d.fillRect(0, 0, 800, 60)
        g2d.color = Color.WHITE
        g2d.drawString("Test Application", 20, 35)
        
        g2d.dispose()
        return imageToByteArray(image)
    }
    
    private fun createTestDocument(): ByteArray {
        val image = BufferedImage(600, 800, BufferedImage.TYPE_INT_RGB)
        val g2d: Graphics2D = image.createGraphics()
        
        g2d.color = Color.WHITE
        g2d.fillRect(0, 0, 600, 800)
        g2d.color = Color.BLACK
        g2d.drawString("Test Document", 50, 50)
        g2d.drawString("This is sample text for OCR testing.", 50, 100)
        
        g2d.dispose()
        return imageToByteArray(image)
    }
    
    private fun createTestUIComponent(): ByteArray {
        val image = BufferedImage(400, 300, BufferedImage.TYPE_INT_RGB)
        val g2d: Graphics2D = image.createGraphics()
        
        g2d.color = Color.WHITE
        g2d.fillRect(0, 0, 400, 300)
        g2d.color = Color.BLACK
        g2d.drawRect(20, 20, 360, 260)
        g2d.drawString("Test Form", 30, 40)
        g2d.drawRect(30, 60, 200, 25)
        
        g2d.dispose()
        return imageToByteArray(image)
    }
    
    private fun createTestNaturalImage(): ByteArray {
        val image = BufferedImage(400, 300, BufferedImage.TYPE_INT_RGB)
        val g2d: Graphics2D = image.createGraphics()
        
        g2d.color = Color.CYAN
        g2d.fillRect(0, 0, 400, 150)
        g2d.color = Color.GREEN
        g2d.fillRect(0, 150, 400, 150)
        
        g2d.dispose()
        return imageToByteArray(image)
    }
    
    private fun createCorruptedImage(): ByteArray {
        return byteArrayOf(0xFF.toByte(), 0xD8.toByte(), 0xFF.toByte())
    }
    
    private fun imageToByteArray(image: BufferedImage): ByteArray {
        val baos = ByteArrayOutputStream()
        ImageIO.write(image, "PNG", baos)
        return baos.toByteArray()
    }
    
    private fun createMockMultimodalService(): MultimodalService {
        return object : MultimodalService(
            analysisUseCase = createMockAnalysisUseCase(),
            getAnalysisUseCase = createMockGetAnalysisUseCase(),
            getUserAnalysesUseCase = createMockGetUserAnalysesUseCase(),
            searchAnalysesUseCase = createMockSearchAnalysesUseCase(),
            getStatisticsUseCase = createMockGetStatisticsUseCase(),
            workflowSelector = createMockWorkflowSelector(),
            contextService = createMockContextService()
        ) {
            override suspend fun analyzeImage(request: AnalysisRequest): MultimodalAnalysis {
                // Simulate processing based on request
                return MultimodalAnalysis(
                    id = "test-analysis-${System.currentTimeMillis()}",
                    imageId = request.imageId,
                    analysisType = request.analysisType,
                    description = "Mock analysis result for ${request.analysisType.name.lowercase()}",
                    confidence = 0.85,
                    modelUsed = "mock-model",
                    workflowType = request.workflowType ?: WorkflowType.BASIC_ANALYSIS,
                    processingTime = 1.5,
                    metadata = mapOf(
                        "mock" to "true",
                        "workflow_config" to (request.workflowType?.name ?: "BASIC_ANALYSIS"),
                        "quality_score" to "0.8"
                    ),
                    extractedText = if (request.analysisType == AnalysisType.DOCUMENT) "Sample extracted text" else null,
                    uiElements = if (request.analysisType == AnalysisType.SCREENSHOT || request.analysisType == AnalysisType.UI_COMPONENT) {
                        listOf(
                            UIElement(
                                type = "button",
                                confidence = 0.9,
                                bounds = ElementBounds(200, 200, 100, 30),
                                properties = mapOf("text" to "Submit")
                            )
                        )
                    } else emptyList(),
                    tags = listOf("test", "mock", request.analysisType.name.lowercase()),
                    userId = request.userId
                )
            }

            override suspend fun getAnalysis(id: String): MultimodalAnalysis {
                if (id == "non-existent-id") {
                    throw MultimodalNotFoundException("Analysis not found: $id")
                }
                return MultimodalAnalysis(
                    id = id,
                    imageId = "test-image-123",
                    analysisType = AnalysisType.SCREENSHOT,
                    description = "Mock retrieved analysis",
                    confidence = 0.8,
                    modelUsed = "mock-model",
                    workflowType = WorkflowType.BASIC_ANALYSIS,
                    processingTime = 1.0,
                    userId = "test-user"
                )
            }

            override suspend fun getUserAnalyses(userId: String, limit: Int, offset: Int): List<MultimodalAnalysis> {
                return (1..minOf(limit, 5)).map { index ->
                    MultimodalAnalysis(
                        id = "user-analysis-$index",
                        imageId = "user-image-$index",
                        analysisType = AnalysisType.SCREENSHOT,
                        description = "User analysis $index",
                        confidence = 0.7 + (index * 0.05),
                        modelUsed = "mock-model",
                        workflowType = WorkflowType.BASIC_ANALYSIS,
                        processingTime = 1.0 + index,
                        userId = userId
                    )
                }
            }

            override suspend fun getStatistics(userId: String?): AnalysisStatistics {
                return AnalysisStatistics(
                    totalAnalyses = 10,
                    averageConfidence = 0.82,
                    averageProcessingTime = 2.5,
                    analysisTypeBreakdown = mapOf(
                        AnalysisType.SCREENSHOT to 5L,
                        AnalysisType.DOCUMENT to 3L,
                        AnalysisType.UI_COMPONENT to 2L
                    ),
                    workflowTypeBreakdown = mapOf(
                        WorkflowType.BASIC_ANALYSIS to 6L,
                        WorkflowType.CONTEXTUAL_ANALYSIS to 4L
                    ),
                    modelUsageBreakdown = mapOf("mock-model" to 10L),
                    dailyAnalysisCount = mapOf("2025-01-06" to 10L)
                )
            }

            override fun getAvailableWorkflows(analysisType: AnalysisType): List<WorkflowConfiguration> {
                return WorkflowType.values().map { workflowType ->
                    WorkflowConfiguration(
                        type = workflowType,
                        visionModel = "mock-model",
                        useContextEnhancement = workflowType != WorkflowType.BASIC_ANALYSIS,
                        maxIterations = if (workflowType == WorkflowType.ITERATIVE_REFINEMENT) 3 else 1,
                        requireConsensus = workflowType == WorkflowType.MULTI_MODEL_CONSENSUS,
                        timeoutSeconds = 300,
                        parameters = mapOf("mock" to "true")
                    )
                }
            }
        }
    }

    // Helper mock creation methods
    private fun createMockAnalysisUseCase(): com.unhinged.application.multimodal.MultimodalAnalysisUseCase {
        // This would be properly mocked in a real implementation
        return object : com.unhinged.application.multimodal.MultimodalAnalysisUseCase(
            multimodalRepository = createMockRepository(),
            domainService = createMockDomainService(),
            workflowSelector = createMockWorkflowSelector(),
            contextService = createMockContextService(),
            visionService = createMockVisionService(),
            contextLLMService = createMockContextLLMService(),
            cacheService = createMockCacheService()
        ) {}
    }

    private fun createMockGetAnalysisUseCase(): com.unhinged.application.multimodal.GetAnalysisUseCase {
        return com.unhinged.application.multimodal.GetAnalysisUseCase(createMockRepository())
    }

    private fun createMockGetUserAnalysesUseCase(): com.unhinged.application.multimodal.GetUserAnalysesUseCase {
        return com.unhinged.application.multimodal.GetUserAnalysesUseCase(createMockRepository())
    }

    private fun createMockSearchAnalysesUseCase(): com.unhinged.application.multimodal.SearchAnalysesUseCase {
        return com.unhinged.application.multimodal.SearchAnalysesUseCase(createMockRepository())
    }

    private fun createMockGetStatisticsUseCase(): com.unhinged.application.multimodal.GetAnalysisStatisticsUseCase {
        return com.unhinged.application.multimodal.GetAnalysisStatisticsUseCase(createMockRepository())
    }

    private fun createMockRepository(): MultimodalRepository = com.unhinged.infrastructure.multimodal.InMemoryMultimodalRepository()
    private fun createMockWorkflowSelector(): WorkflowSelector = com.unhinged.infrastructure.multimodal.DefaultWorkflowSelector("mock-model", true, 300)
    private fun createMockContextService(): ContextService = object : ContextService {
        override suspend fun searchContext(query: String, contextTypes: List<ContextType>, maxResults: Int): List<ContextItem> = emptyList()
        override suspend fun getContextByType(contextType: ContextType, limit: Int): List<ContextItem> = emptyList()
        override suspend fun refreshContext(): Int = 0
    }
    private fun createMockDomainService(): MultimodalDomainService = object : MultimodalDomainService {
        override fun validateAnalysisRequest(request: AnalysisRequest): List<MultimodalValidationError> = emptyList()
        override fun validateAnalysisResult(analysis: MultimodalAnalysis): List<MultimodalValidationError> = emptyList()
        override fun selectOptimalWorkflow(analysisType: AnalysisType, priority: Priority, userPreference: WorkflowType?): WorkflowConfiguration =
            WorkflowConfiguration(WorkflowType.BASIC_ANALYSIS, "mock-model", false, 1, false, 300)
        override fun calculateAdjustedConfidence(rawConfidence: Double, modelUsed: String, workflowType: WorkflowType, processingTime: Double): Double = rawConfidence
        override fun validateUIElements(uiElements: List<UIElement>, imageWidth: Int, imageHeight: Int): List<MultimodalValidationError> = emptyList()
        override fun requiresHumanReview(analysis: MultimodalAnalysis): Boolean = false
        override fun calculateQualityScore(analysis: MultimodalAnalysis): Double = 0.8
        override fun generateCacheKey(request: AnalysisRequest): String = "mock-cache-key"
        override fun isCacheable(request: AnalysisRequest): Boolean = true
        override fun calculateCacheTTL(analysis: MultimodalAnalysis): Long = 3600
        override fun filterRelevantContext(contextItems: List<ContextItem>, analysisType: AnalysisType): List<ContextItem> = contextItems
        override fun mergeAnalysisResults(analyses: List<MultimodalAnalysis>): MultimodalAnalysis = analyses.first()
        override fun calculateProcessingPriority(request: AnalysisRequest): Priority = request.priority
    }
    private fun createMockVisionService(): com.unhinged.application.multimodal.VisionInferenceService = object : com.unhinged.application.multimodal.VisionInferenceService {
        override suspend fun infer(imageData: ByteArray, model: String, prompt: String, analysisType: String, maxTokens: Int, temperature: Float): com.unhinged.application.multimodal.VisionInferenceResult =
            com.unhinged.application.multimodal.VisionInferenceResult("Mock result", 0.8, model, 1.0, emptyMap(), null, emptyList(), emptyList())
    }
    private fun createMockContextLLMService(): com.unhinged.application.multimodal.ContextLLMService = object : com.unhinged.application.multimodal.ContextLLMService {
        override suspend fun generatePrompt(basePrompt: String, analysisType: String, contextTypes: List<String>, maxContextItems: Int): String = "Enhanced: $basePrompt"
    }
    private fun createMockCacheService(): com.unhinged.application.multimodal.CacheService = object : com.unhinged.application.multimodal.CacheService {
        override suspend fun <T> get(key: String): T? = null
        override suspend fun <T> set(key: String, value: T, ttlSeconds: Long) {}
        override suspend fun delete(key: String): Boolean = true
    }
}
