// ============================================================================
// Default Workflow Selector - Infrastructure Layer
// ============================================================================
//
// @file DefaultWorkflowSelector.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Default implementation of workflow selection logic
//
// This implementation provides intelligent workflow selection based on
// analysis type, priority, and system capabilities.
//
// ============================================================================

package com.unhinged.infrastructure.multimodal

import com.unhinged.domain.multimodal.*
import org.springframework.beans.factory.annotation.Value
import org.springframework.stereotype.Component

// ============================================================================
// Default Workflow Selector
// ============================================================================

/**
 * Default implementation of WorkflowSelector
 * 
 * Provides intelligent workflow selection based on analysis requirements,
 * system load, and available resources.
 */
@Component
class DefaultWorkflowSelector(
    @Value("\${multimodal.default-vision-model:qwen2-vl}")
    private val defaultVisionModel: String,
    @Value("\${multimodal.enable-context-enhancement:true}")
    private val enableContextEnhancement: Boolean,
    @Value("\${multimodal.default-timeout:300}")
    private val defaultTimeoutSeconds: Int
) : WorkflowSelector {
    
    override fun selectOptimalWorkflow(
        analysisType: AnalysisType,
        priority: Priority,
        userPreference: WorkflowType?
    ): WorkflowConfiguration {
        
        // Honor user preference if provided and valid
        userPreference?.let { preference ->
            return createWorkflowConfiguration(preference, analysisType, priority)
        }
        
        // Select based on analysis type and priority
        val optimalWorkflowType = when (analysisType) {
            AnalysisType.SCREENSHOT -> selectScreenshotWorkflow(priority)
            AnalysisType.UI_COMPONENT -> selectUIComponentWorkflow(priority)
            AnalysisType.DOCUMENT -> selectDocumentWorkflow(priority)
            AnalysisType.OCR_FOCUSED -> selectOCRWorkflow(priority)
            AnalysisType.NATURAL_IMAGE -> selectNaturalImageWorkflow(priority)
        }
        
        return createWorkflowConfiguration(optimalWorkflowType, analysisType, priority)
    }
    
    override fun getAvailableWorkflows(analysisType: AnalysisType): List<WorkflowConfiguration> {
        return WorkflowType.values().map { workflowType ->
            createWorkflowConfiguration(workflowType, analysisType, Priority.NORMAL)
        }
    }
    
    override fun getDefaultWorkflow(analysisType: AnalysisType): WorkflowConfiguration {
        return selectOptimalWorkflow(analysisType, Priority.NORMAL, null)
    }
    
    /**
     * Select workflow for screenshot analysis
     */
    private fun selectScreenshotWorkflow(priority: Priority): WorkflowType {
        return when (priority) {
            Priority.LOW -> WorkflowType.BASIC_ANALYSIS
            Priority.NORMAL -> WorkflowType.CONTEXTUAL_ANALYSIS
            Priority.HIGH -> WorkflowType.ITERATIVE_REFINEMENT
            Priority.CRITICAL -> WorkflowType.MULTI_MODEL_CONSENSUS
        }
    }
    
    /**
     * Select workflow for UI component analysis
     */
    private fun selectUIComponentWorkflow(priority: Priority): WorkflowType {
        return when (priority) {
            Priority.LOW -> WorkflowType.BASIC_ANALYSIS
            Priority.NORMAL, Priority.HIGH -> WorkflowType.CONTEXTUAL_ANALYSIS
            Priority.CRITICAL -> WorkflowType.ITERATIVE_REFINEMENT
        }
    }
    
    /**
     * Select workflow for document analysis
     */
    private fun selectDocumentWorkflow(priority: Priority): WorkflowType {
        return when (priority) {
            Priority.LOW -> WorkflowType.BASIC_ANALYSIS
            Priority.NORMAL -> WorkflowType.CONTEXTUAL_ANALYSIS
            Priority.HIGH, Priority.CRITICAL -> WorkflowType.ITERATIVE_REFINEMENT
        }
    }
    
    /**
     * Select workflow for OCR-focused analysis
     */
    private fun selectOCRWorkflow(priority: Priority): WorkflowType {
        return when (priority) {
            Priority.LOW, Priority.NORMAL -> WorkflowType.BASIC_ANALYSIS
            Priority.HIGH -> WorkflowType.CONTEXTUAL_ANALYSIS
            Priority.CRITICAL -> WorkflowType.ITERATIVE_REFINEMENT
        }
    }
    
    /**
     * Select workflow for natural image analysis
     */
    private fun selectNaturalImageWorkflow(priority: Priority): WorkflowType {
        return when (priority) {
            Priority.LOW -> WorkflowType.BASIC_ANALYSIS
            Priority.NORMAL -> WorkflowType.CONTEXTUAL_ANALYSIS
            Priority.HIGH -> WorkflowType.ITERATIVE_REFINEMENT
            Priority.CRITICAL -> WorkflowType.MULTI_MODEL_CONSENSUS
        }
    }
    
    /**
     * Create workflow configuration for given parameters
     */
    private fun createWorkflowConfiguration(
        workflowType: WorkflowType,
        analysisType: AnalysisType,
        priority: Priority
    ): WorkflowConfiguration {
        
        val visionModel = selectVisionModel(analysisType, workflowType)
        val useContextEnhancement = shouldUseContextEnhancement(workflowType, analysisType)
        val maxIterations = getMaxIterations(workflowType, priority)
        val requireConsensus = shouldRequireConsensus(workflowType)
        val timeoutSeconds = calculateTimeout(workflowType, priority)
        
        return WorkflowConfiguration(
            type = workflowType,
            visionModel = visionModel,
            useContextEnhancement = useContextEnhancement,
            maxIterations = maxIterations,
            requireConsensus = requireConsensus,
            timeoutSeconds = timeoutSeconds,
            parameters = createWorkflowParameters(workflowType, analysisType, priority)
        )
    }
    
    /**
     * Select appropriate vision model for analysis
     */
    private fun selectVisionModel(analysisType: AnalysisType, workflowType: WorkflowType): String {
        return when (analysisType) {
            AnalysisType.SCREENSHOT, AnalysisType.UI_COMPONENT -> "qwen2-vl" // Best for UI analysis
            AnalysisType.DOCUMENT, AnalysisType.OCR_FOCUSED -> "qwen2-vl" // Good OCR capabilities
            AnalysisType.NATURAL_IMAGE -> when (workflowType) {
                WorkflowType.BASIC_ANALYSIS -> "blip-base" // Faster for simple cases
                else -> "qwen2-vl" // Better quality for complex analysis
            }
        }
    }
    
    /**
     * Determine if context enhancement should be used
     */
    private fun shouldUseContextEnhancement(workflowType: WorkflowType, analysisType: AnalysisType): Boolean {
        if (!enableContextEnhancement) return false
        
        return when (workflowType) {
            WorkflowType.BASIC_ANALYSIS -> false
            WorkflowType.CONTEXTUAL_ANALYSIS, 
            WorkflowType.ITERATIVE_REFINEMENT, 
            WorkflowType.MULTI_MODEL_CONSENSUS -> when (analysisType) {
                AnalysisType.SCREENSHOT, AnalysisType.UI_COMPONENT -> true
                AnalysisType.DOCUMENT -> true
                AnalysisType.OCR_FOCUSED -> false // OCR doesn't benefit much from context
                AnalysisType.NATURAL_IMAGE -> false // Natural images don't need project context
            }
        }
    }
    
    /**
     * Get maximum iterations for workflow
     */
    private fun getMaxIterations(workflowType: WorkflowType, priority: Priority): Int {
        return when (workflowType) {
            WorkflowType.BASIC_ANALYSIS -> 1
            WorkflowType.CONTEXTUAL_ANALYSIS -> 1
            WorkflowType.ITERATIVE_REFINEMENT -> when (priority) {
                Priority.LOW -> 2
                Priority.NORMAL -> 3
                Priority.HIGH -> 4
                Priority.CRITICAL -> 5
            }
            WorkflowType.MULTI_MODEL_CONSENSUS -> 1 // Multiple models, not iterations
        }
    }
    
    /**
     * Determine if consensus is required
     */
    private fun shouldRequireConsensus(workflowType: WorkflowType): Boolean {
        return workflowType == WorkflowType.MULTI_MODEL_CONSENSUS
    }
    
    /**
     * Calculate timeout based on workflow and priority
     */
    private fun calculateTimeout(workflowType: WorkflowType, priority: Priority): Int {
        val baseTimeout = when (workflowType) {
            WorkflowType.BASIC_ANALYSIS -> 60 // 1 minute
            WorkflowType.CONTEXTUAL_ANALYSIS -> 120 // 2 minutes
            WorkflowType.ITERATIVE_REFINEMENT -> 300 // 5 minutes
            WorkflowType.MULTI_MODEL_CONSENSUS -> 180 // 3 minutes
        }
        
        return when (priority) {
            Priority.LOW -> (baseTimeout * 0.8).toInt()
            Priority.NORMAL -> baseTimeout
            Priority.HIGH -> (baseTimeout * 1.2).toInt()
            Priority.CRITICAL -> (baseTimeout * 1.5).toInt()
        }
    }
    
    /**
     * Create workflow-specific parameters
     */
    private fun createWorkflowParameters(
        workflowType: WorkflowType,
        analysisType: AnalysisType,
        priority: Priority
    ): Map<String, Any> {
        return mapOf(
            "analysis_type" to analysisType.name.lowercase(),
            "priority" to priority.name.lowercase(),
            "workflow_type" to workflowType.name.lowercase(),
            "enable_caching" to (priority != Priority.CRITICAL),
            "temperature" to when (workflowType) {
                WorkflowType.BASIC_ANALYSIS -> 0.1
                WorkflowType.CONTEXTUAL_ANALYSIS -> 0.2
                WorkflowType.ITERATIVE_REFINEMENT -> 0.1
                WorkflowType.MULTI_MODEL_CONSENSUS -> 0.15
            },
            "max_tokens" to when (analysisType) {
                AnalysisType.SCREENSHOT, AnalysisType.UI_COMPONENT -> 1024
                AnalysisType.DOCUMENT -> 2048
                AnalysisType.OCR_FOCUSED -> 512
                AnalysisType.NATURAL_IMAGE -> 1024
            }
        )
    }
}
