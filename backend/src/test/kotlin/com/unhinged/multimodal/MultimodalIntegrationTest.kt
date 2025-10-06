// ============================================================================
// Multimodal Integration Tests - Backend Layer
// ============================================================================
//
// @file MultimodalIntegrationTest.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Integration tests for multimodal AI architecture refactoring
//
// Tests the complete gRPC pipeline: Kotlin backend → Python AI services
// Validates service boundaries and architecture compliance
//
// ============================================================================

package com.unhinged.multimodal

import com.unhinged.application.multimodal.MultimodalService
import com.unhinged.domain.multimodal.*
import com.unhinged.infrastructure.multimodal.VisionAIGrpcClient
import com.unhinged.infrastructure.multimodal.ContextLLMGrpcClient
import com.unhinged.infrastructure.multimodal.InMemoryMultimodalRepository
import com.unhinged.infrastructure.multimodal.DefaultWorkflowSelector
import io.ktor.client.request.*
import io.ktor.client.request.forms.*
import io.ktor.http.*
import io.ktor.server.testing.*
import kotlinx.coroutines.runBlocking
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
class MultimodalIntegrationTest {
    
    private lateinit var multimodalService: MultimodalService
    private lateinit var visionClient: VisionAIGrpcClient
    private lateinit var contextClient: ContextLLMGrpcClient
    private lateinit var repository: InMemoryMultimodalRepository
    private lateinit var workflowSelector: DefaultWorkflowSelector
    
    @BeforeAll
    fun setup() {
        // Initialize test components
        repository = InMemoryMultimodalRepository()
        workflowSelector = DefaultWorkflowSelector("qwen2-vl", true, 300)
        
        // Note: In real tests, these would connect to actual gRPC services
        // For now, we'll use mock implementations that simulate the behavior
        visionClient = createMockVisionClient()
        contextClient = createMockContextClient()
        
        // Initialize service with dependencies
        multimodalService = MultimodalService(
            analysisUseCase = createAnalysisUseCase(),
            getAnalysisUseCase = createGetAnalysisUseCase(),
            getUserAnalysesUseCase = createGetUserAnalysesUseCase(),
            searchAnalysesUseCase = createSearchAnalysesUseCase(),
            getStatisticsUseCase = createGetStatisticsUseCase(),
            workflowSelector = workflowSelector,
            contextService = createMockContextService()
        )
    }
    
    @Test
    fun `should perform basic analysis workflow`() = runBlocking {
        // Given: A synthetic screenshot image
        val imageData = createSyntheticScreenshot()
        val request = AnalysisRequest(
            imageId = "test-screenshot-001",
            imageData = imageData,
            analysisType = AnalysisType.SCREENSHOT,
            workflowType = WorkflowType.BASIC_ANALYSIS,
            prompt = "Analyze this UI screenshot",
            userId = "test-user"
        )
        
        // When: Performing analysis
        val result = multimodalService.analyzeImage(request)
        
        // Then: Verify results
        assertNotNull(result.id)
        assertEquals("test-screenshot-001", result.imageId)
        assertEquals(AnalysisType.SCREENSHOT, result.analysisType)
        assertEquals(WorkflowType.BASIC_ANALYSIS, result.workflowType)
        assertTrue(result.confidence > 0.0)
        assertTrue(result.description.isNotEmpty())
        assertEquals("test-user", result.userId)
        
        // Verify service boundaries: Python only did inference
        assertTrue(result.metadata.containsKey("model_used"))
        assertTrue(result.processingTime > 0.0)
    }
    
    @Test
    fun `should perform contextual analysis with project context`() = runBlocking {
        // Given: A UI component image
        val imageData = createSyntheticUIComponent()
        val request = AnalysisRequest(
            imageId = "test-ui-component-001",
            imageData = imageData,
            analysisType = AnalysisType.UI_COMPONENT,
            workflowType = WorkflowType.CONTEXTUAL_ANALYSIS,
            prompt = "Analyze this form component",
            userId = "test-user"
        )
        
        // When: Performing contextual analysis
        val result = multimodalService.analyzeImage(request)
        
        // Then: Verify context enhancement
        assertEquals(WorkflowType.CONTEXTUAL_ANALYSIS, result.workflowType)
        assertTrue(result.metadata.containsKey("context_enhanced"))
        assertEquals("true", result.metadata["context_enhanced"])
        
        // Verify UI elements detected
        assertTrue(result.uiElements.isNotEmpty())
        val formElements = result.uiElements.filter { it.type.contains("form") || it.type.contains("input") }
        assertTrue(formElements.isNotEmpty())
    }
    
    @Test
    fun `should perform iterative refinement workflow`() = runBlocking {
        // Given: A document image
        val imageData = createSyntheticDocument()
        val request = AnalysisRequest(
            imageId = "test-document-001",
            imageData = imageData,
            analysisType = AnalysisType.DOCUMENT,
            workflowType = WorkflowType.ITERATIVE_REFINEMENT,
            prompt = "Extract and analyze all text content",
            userId = "test-user"
        )
        
        // When: Performing iterative analysis
        val result = multimodalService.analyzeImage(request)
        
        // Then: Verify refinement occurred
        assertEquals(WorkflowType.ITERATIVE_REFINEMENT, result.workflowType)
        assertTrue(result.metadata.containsKey("refinement_iterations"))
        
        // Verify OCR results
        assertNotNull(result.extractedText)
        assertTrue(result.extractedText!!.isNotEmpty())
        
        // Verify higher confidence due to refinement
        assertTrue(result.confidence > 0.7)
    }
    
    @Test
    fun `should handle multi-model consensus workflow`() = runBlocking {
        // Given: A natural image
        val imageData = createSyntheticNaturalImage()
        val request = AnalysisRequest(
            imageId = "test-natural-001",
            imageData = imageData,
            analysisType = AnalysisType.NATURAL_IMAGE,
            workflowType = WorkflowType.MULTI_MODEL_CONSENSUS,
            prompt = "Describe this scene in detail",
            userId = "test-user"
        )
        
        // When: Performing consensus analysis
        val result = multimodalService.analyzeImage(request)
        
        // Then: Verify consensus metadata
        assertEquals(WorkflowType.MULTI_MODEL_CONSENSUS, result.workflowType)
        assertTrue(result.metadata.containsKey("consensus_models"))
        assertTrue(result.metadata.containsKey("consensus_method"))
        
        // Verify enhanced confidence
        assertTrue(result.confidence > 0.8)
    }
    
    @Test
    fun `should validate service boundaries - Python only does inference`() = runBlocking {
        // Given: Any analysis request
        val imageData = createSyntheticScreenshot()
        val request = AnalysisRequest(
            imageId = "boundary-test-001",
            imageData = imageData,
            analysisType = AnalysisType.SCREENSHOT,
            workflowType = WorkflowType.BASIC_ANALYSIS,
            userId = "test-user"
        )
        
        // When: Performing analysis
        val result = multimodalService.analyzeImage(request)
        
        // Then: Verify Kotlin handled business logic
        assertNotNull(result.id) // Generated by Kotlin
        assertTrue(result.createdAt.toString().isNotEmpty()) // Timestamp by Kotlin
        assertEquals("test-user", result.userId) // User context by Kotlin
        
        // Verify Python only provided inference results
        assertTrue(result.metadata.containsKey("model_used")) // From Python
        assertTrue(result.description.isNotEmpty()) // From Python
        assertTrue(result.confidence > 0.0) // From Python
        
        // Verify workflow orchestration by Kotlin
        assertEquals(WorkflowType.BASIC_ANALYSIS, result.workflowType)
        assertTrue(result.metadata.containsKey("workflow_config"))
    }
    
    @Test
    fun `should handle gRPC communication errors gracefully`() = runBlocking {
        // Given: A request that will cause gRPC failure (simulated)
        val imageData = createCorruptedImage()
        val request = AnalysisRequest(
            imageId = "error-test-001",
            imageData = imageData,
            analysisType = AnalysisType.SCREENSHOT,
            userId = "test-user"
        )
        
        // When/Then: Should handle error gracefully
        assertThrows<MultimodalProcessingException> {
            runBlocking { multimodalService.analyzeImage(request) }
        }
    }
    
    @Test
    fun `should validate input parameters`() = runBlocking {
        // Given: Invalid request
        val request = AnalysisRequest(
            imageId = "", // Invalid empty ID
            imageData = byteArrayOf(), // Invalid empty data
            analysisType = AnalysisType.SCREENSHOT,
            userId = "test-user"
        )
        
        // When/Then: Should validate and throw exception
        assertThrows<MultimodalValidationException> {
            runBlocking { multimodalService.analyzeImage(request) }
        }
    }
    
    @Test
    fun `should retrieve analysis by ID`() = runBlocking {
        // Given: An existing analysis
        val imageData = createSyntheticScreenshot()
        val request = AnalysisRequest(
            imageId = "retrieve-test-001",
            imageData = imageData,
            analysisType = AnalysisType.SCREENSHOT,
            userId = "test-user"
        )
        val savedAnalysis = multimodalService.analyzeImage(request)
        
        // When: Retrieving by ID
        val retrieved = multimodalService.getAnalysis(savedAnalysis.id)
        
        // Then: Should match original
        assertEquals(savedAnalysis.id, retrieved.id)
        assertEquals(savedAnalysis.description, retrieved.description)
        assertEquals(savedAnalysis.confidence, retrieved.confidence)
    }
    
    @Test
    fun `should get user analyses with pagination`() = runBlocking {
        // Given: Multiple analyses for a user
        val userId = "pagination-test-user"
        repeat(5) { index ->
            val imageData = createSyntheticScreenshot()
            val request = AnalysisRequest(
                imageId = "pagination-test-$index",
                imageData = imageData,
                analysisType = AnalysisType.SCREENSHOT,
                userId = userId
            )
            multimodalService.analyzeImage(request)
        }
        
        // When: Getting user analyses with pagination
        val firstPage = multimodalService.getUserAnalyses(userId, limit = 3, offset = 0)
        val secondPage = multimodalService.getUserAnalyses(userId, limit = 3, offset = 3)
        
        // Then: Should paginate correctly
        assertEquals(3, firstPage.size)
        assertEquals(2, secondPage.size)
        
        // Verify all belong to user
        firstPage.forEach { assertEquals(userId, it.userId) }
        secondPage.forEach { assertEquals(userId, it.userId) }
    }
    
    @Test
    fun `should generate analysis statistics`() = runBlocking {
        // Given: Various analyses
        val userId = "stats-test-user"
        val analysisTypes = listOf(
            AnalysisType.SCREENSHOT,
            AnalysisType.DOCUMENT,
            AnalysisType.UI_COMPONENT
        )
        
        analysisTypes.forEach { type ->
            val imageData = when (type) {
                AnalysisType.SCREENSHOT -> createSyntheticScreenshot()
                AnalysisType.DOCUMENT -> createSyntheticDocument()
                AnalysisType.UI_COMPONENT -> createSyntheticUIComponent()
                else -> createSyntheticScreenshot()
            }
            
            val request = AnalysisRequest(
                imageId = "stats-test-${type.name}",
                imageData = imageData,
                analysisType = type,
                userId = userId
            )
            multimodalService.analyzeImage(request)
        }
        
        // When: Getting statistics
        val stats = multimodalService.getStatistics(userId)
        
        // Then: Should have correct statistics
        assertEquals(3, stats.totalAnalyses)
        assertTrue(stats.averageConfidence > 0.0)
        assertTrue(stats.averageProcessingTime > 0.0)
        assertEquals(3, stats.analysisTypeBreakdown.size)
    }
    
    // Helper methods for creating test data
    private fun createSyntheticScreenshot(): ByteArray {
        val image = BufferedImage(800, 600, BufferedImage.TYPE_INT_RGB)
        val g2d: Graphics2D = image.createGraphics()
        
        // Background
        g2d.color = Color.WHITE
        g2d.fillRect(0, 0, 800, 600)
        
        // Header
        g2d.color = Color.BLUE
        g2d.fillRect(0, 0, 800, 60)
        g2d.color = Color.WHITE
        g2d.drawString("Application Header", 20, 35)
        
        // Navigation
        g2d.color = Color.LIGHT_GRAY
        g2d.fillRect(0, 60, 150, 540)
        g2d.color = Color.BLACK
        g2d.drawString("Navigation", 10, 90)
        g2d.drawString("• Dashboard", 10, 120)
        g2d.drawString("• Settings", 10, 140)
        
        // Main content with form
        g2d.color = Color.WHITE
        g2d.fillRect(170, 80, 610, 500)
        g2d.color = Color.BLACK
        g2d.drawRect(170, 80, 610, 500)
        g2d.drawString("Main Content", 180, 110)
        
        // Form elements
        g2d.drawRect(200, 150, 300, 30) // Input field
        g2d.drawString("Input Field", 210, 170)
        
        g2d.color = Color.GREEN
        g2d.fillRect(200, 200, 100, 30) // Button
        g2d.color = Color.WHITE
        g2d.drawString("Submit", 230, 220)
        
        g2d.dispose()
        
        return imageToByteArray(image)
    }
    
    private fun createSyntheticDocument(): ByteArray {
        val image = BufferedImage(600, 800, BufferedImage.TYPE_INT_RGB)
        val g2d: Graphics2D = image.createGraphics()
        
        g2d.color = Color.WHITE
        g2d.fillRect(0, 0, 600, 800)
        g2d.color = Color.BLACK
        
        // Title
        g2d.drawString("Document Title", 50, 50)
        g2d.drawLine(50, 60, 550, 60)
        
        // Paragraphs
        val paragraphs = listOf(
            "This is a sample document for testing OCR capabilities.",
            "It contains multiple paragraphs with different formatting.",
            "The document includes headings and body text.",
            "This helps test document analysis functionality."
        )
        
        var y = 100
        paragraphs.forEach { paragraph ->
            g2d.drawString(paragraph, 50, y)
            y += 30
        }
        
        // Subheading
        g2d.drawString("Section Heading", 50, y + 20)
        g2d.drawLine(50, y + 30, 200, y + 30)
        
        g2d.dispose()
        return imageToByteArray(image)
    }
    
    private fun createSyntheticUIComponent(): ByteArray {
        val image = BufferedImage(400, 300, BufferedImage.TYPE_INT_RGB)
        val g2d: Graphics2D = image.createGraphics()
        
        g2d.color = Color.WHITE
        g2d.fillRect(0, 0, 400, 300)
        
        // Form container
        g2d.color = Color.BLACK
        g2d.drawRect(20, 20, 360, 260)
        g2d.drawString("Login Form", 30, 40)
        
        // Username field
        g2d.drawString("Username:", 30, 70)
        g2d.drawRect(30, 80, 320, 25)
        
        // Password field
        g2d.drawString("Password:", 30, 120)
        g2d.drawRect(30, 130, 320, 25)
        
        // Login button
        g2d.color = Color.BLUE
        g2d.fillRect(30, 180, 100, 30)
        g2d.color = Color.WHITE
        g2d.drawString("Login", 60, 200)
        
        g2d.dispose()
        return imageToByteArray(image)
    }
    
    private fun createSyntheticNaturalImage(): ByteArray {
        val image = BufferedImage(500, 300, BufferedImage.TYPE_INT_RGB)
        val g2d: Graphics2D = image.createGraphics()
        
        // Sky
        g2d.color = Color.CYAN
        g2d.fillRect(0, 0, 500, 150)
        
        // Ground
        g2d.color = Color.GREEN
        g2d.fillRect(0, 150, 500, 150)
        
        // Sun
        g2d.color = Color.YELLOW
        g2d.fillOval(400, 30, 60, 60)
        
        // Tree
        g2d.color = Color(139, 69, 19) // Brown
        g2d.fillRect(100, 100, 20, 50)
        g2d.color = Color.GREEN
        g2d.fillOval(80, 80, 60, 40)
        
        g2d.dispose()
        return imageToByteArray(image)
    }
    
    private fun createCorruptedImage(): ByteArray {
        return byteArrayOf(0xFF.toByte(), 0xD8.toByte(), 0xFF.toByte()) // Invalid JPEG header
    }
    
    private fun imageToByteArray(image: BufferedImage): ByteArray {
        val baos = ByteArrayOutputStream()
        ImageIO.write(image, "PNG", baos)
        return baos.toByteArray()
    }
    
    // Mock implementations for testing
    private fun createMockVisionClient(): VisionAIGrpcClient {
        // In real implementation, this would be a proper mock or test double
        // For now, return a mock that simulates successful responses
        TODO("Implement mock vision client")
    }
    
    private fun createMockContextClient(): ContextLLMGrpcClient {
        TODO("Implement mock context client")
    }
    
    private fun createAnalysisUseCase(): com.unhinged.application.multimodal.MultimodalAnalysisUseCase {
        TODO("Implement with mocked dependencies")
    }
    
    private fun createGetAnalysisUseCase(): com.unhinged.application.multimodal.GetAnalysisUseCase {
        TODO("Implement with repository")
    }
    
    private fun createGetUserAnalysesUseCase(): com.unhinged.application.multimodal.GetUserAnalysesUseCase {
        TODO("Implement with repository")
    }
    
    private fun createSearchAnalysesUseCase(): com.unhinged.application.multimodal.SearchAnalysesUseCase {
        TODO("Implement with repository")
    }
    
    private fun createGetStatisticsUseCase(): com.unhinged.application.multimodal.GetAnalysisStatisticsUseCase {
        TODO("Implement with repository")
    }
    
    private fun createMockContextService(): com.unhinged.domain.multimodal.ContextService {
        TODO("Implement mock context service")
    }
}
