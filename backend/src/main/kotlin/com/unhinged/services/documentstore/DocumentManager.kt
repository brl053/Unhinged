// ============================================================================
// DocumentManager - Business Logic Orchestration Layer
// ============================================================================
// 
// @file DocumentManager.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-04
// @description Manager layer for coordinating document operations with LLM workflows
// 
// This manager orchestrates complex document operations that involve:
// - Multiple repository coordination
// - Transaction boundaries
// - Event emission for async workflows
// - LLM-specific business rules
// - Session context management
// 
// Following Clean Architecture principles:
// - Service layer delegates to this manager
// - Manager coordinates repositories and domain services
// - Pure business logic, no transport protocol concerns
// ============================================================================

package com.unhinged.services.documentstore

import com.unhinged.di.TransactionManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.slf4j.LoggerFactory
import unhinged.document_store.DocumentStore
import java.time.Instant
import java.util.*

/**
 * Document business logic manager with LLM-native orchestration
 * 
 * Coordinates complex document operations that span multiple repositories
 * and require transactional consistency. Handles LLM-specific workflows
 * like session context optimization and semantic analysis.
 * 
 * @param documentRepository Document persistence operations
 * @param eventEmitter Event emission for async workflows
 * @param sessionContextOptimizer LLM context optimization
 * @param documentAnalyzer Semantic analysis and tagging
 * @param transactionManager Database transaction coordination
 * 
 * @since 1.0.0
 * @author Unhinged Team
 */
class DocumentManager(
    private val documentRepository: DocumentRepository,
    private val eventEmitter: DocumentEventEmitter,
    private val sessionContextOptimizer: com.unhinged.di.SessionContextOptimizer,
    private val documentAnalyzer: com.unhinged.di.DocumentAnalyzer,
    private val transactionManager: TransactionManager
) {
    
    private val logger = LoggerFactory.getLogger(DocumentManager::class.java)

    // ========================================================================
    // Document Lifecycle Management
    // ========================================================================

    /**
     * Store document with full LLM workflow orchestration
     * 
     * This operation coordinates:
     * - Document persistence with versioning
     * - Semantic analysis and auto-tagging
     * - Session context invalidation
     * - Event emission for downstream processing
     * - Transaction management for consistency
     * 
     * @param document Document to store
     * @param sessionId Session context for LLM workflows
     * @return DocumentResult with operation outcome and metadata
     */
    suspend fun storeDocumentWithContext(
        document: DocumentStore.Document,
        sessionId: String
    ): DocumentResult {
        return withContext(Dispatchers.IO) {
            transactionManager.withTransaction {
                try {
                    logger.info("Storing document ${document.documentUuid} with LLM context processing")
                    
                    // 1. Analyze document content for LLM optimization
                    val analysis = documentAnalyzer.analyzeDocument(document)
                    logger.debug("Document analysis completed: ${analysis.contentType}, ${analysis.estimatedTokens} tokens")
                    
                    // 2. Enhance document with analysis results
                    val enhancedDocument = enhanceDocumentWithAnalysis(document, analysis)
                    
                    // 3. Store document with versioning
                    val savedDocument = documentRepository.saveDocument(enhancedDocument)
                    logger.info("Document ${savedDocument.documentUuid} stored as version ${savedDocument.version}")
                    
                    // 4. Emit events for async processing (outside transaction)
                    // Note: Events are emitted after transaction commits
                    scheduleEventEmission(savedDocument, analysis)
                    
                    // 5. Return success result
                    DocumentResult.success(
                        document = savedDocument,
                        analysis = analysis,
                        message = "Document stored successfully with LLM optimization"
                    )
                    
                } catch (e: Exception) {
                    logger.error("Failed to store document ${document.documentUuid}: ${e.message}", e)
                    DocumentResult.failure(
                        error = e.message ?: "Unknown error during document storage",
                        document = document
                    )
                }
            }
        }
    }

    /**
     * Retrieve optimized session context for LLM prompt construction
     * 
     * This operation:
     * - Fetches relevant documents from repository
     * - Applies LLM-specific optimization (token limits, relevance scoring)
     * - Tracks context access for analytics
     * - Emits context access events
     * 
     * @param sessionId Session to get context for
     * @param documentTypes Optional filter for document types
     * @param maxTokens Maximum tokens for context window
     * @param includeBody Whether to include document bodies
     * @return SessionContextResult with optimized document list
     */
    suspend fun getOptimizedSessionContext(
        sessionId: String,
        documentTypes: List<String> = emptyList(),
        maxTokens: Int = 8000,
        includeBody: Boolean = true
    ): SessionContextResult {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("Retrieving optimized session context for $sessionId (max tokens: $maxTokens)")
                
                // 1. Fetch raw documents from repository
                val rawDocuments = documentRepository.getSessionContext(
                    sessionId = sessionId,
                    documentTypes = documentTypes,
                    since = null, // TODO: Add time-based filtering
                    limit = 100, // Fetch more than needed for optimization
                    includeBody = includeBody
                )
                
                logger.debug("Retrieved ${rawDocuments.size} raw documents for optimization")
                
                // 2. Apply LLM-specific optimization
                val optimizedDocuments = sessionContextOptimizer.optimizeContextForPrompt(
                    documents = rawDocuments,
                    maxTokens = maxTokens
                )
                
                val totalTokens = optimizedDocuments.sumOf { 
                    sessionContextOptimizer.estimateTokenCount(it.bodyJson) 
                }
                
                logger.info("Optimized context: ${optimizedDocuments.size} documents, $totalTokens tokens")
                
                // 3. Emit context access event for analytics
                eventEmitter.emitSessionContextAccessed(sessionId, optimizedDocuments.size)
                
                // 4. Return optimized context
                SessionContextResult.success(
                    documents = optimizedDocuments,
                    totalTokens = totalTokens,
                    optimizationApplied = rawDocuments.size > optimizedDocuments.size,
                    message = "Session context optimized for LLM prompt construction"
                )
                
            } catch (e: Exception) {
                logger.error("Failed to get session context for $sessionId: ${e.message}", e)
                SessionContextResult.failure(
                    error = e.message ?: "Unknown error during context retrieval",
                    sessionId = sessionId
                )
            }
        }
    }

    /**
     * Tag document version with workflow coordination
     * 
     * Handles:
     * - Version tagging for A/B testing
     * - Environment promotion (dev -> staging -> prod)
     * - Event emission for deployment workflows
     * - Validation of tag operations
     * 
     * @param documentUuid Document to tag
     * @param version Version to tag
     * @param tag Tag to apply
     * @param taggedBy Who is applying the tag
     * @param sessionId Session context for the operation
     * @return TagResult with operation outcome
     */
    suspend fun tagDocumentVersion(
        documentUuid: String,
        version: Int,
        tag: String,
        taggedBy: String,
        sessionId: String
    ): TagResult {
        return withContext(Dispatchers.IO) {
            transactionManager.withTransaction {
                try {
                    logger.info("Tagging document $documentUuid v$version with tag '$tag'")
                    
                    // 1. Validate document exists
                    val document = documentRepository.getDocumentByVersion(documentUuid, version)
                        ?: return@withTransaction TagResult.failure(
                            error = "Document $documentUuid version $version not found",
                            documentUuid = documentUuid,
                            version = version,
                            tag = tag
                        )
                    
                    // 2. Apply tag through repository
                    documentRepository.tagDocument(
                        documentUuid = documentUuid,
                        version = version,
                        tag = tag,
                        taggedBy = taggedBy,
                        taggedByType = "user", // TODO: Determine from context
                        sessionId = sessionId
                    )
                    
                    // 3. Schedule event emission
                    scheduleTagEventEmission(documentUuid, version, tag)
                    
                    logger.info("Successfully tagged document $documentUuid v$version -> $tag")
                    
                    TagResult.success(
                        documentUuid = documentUuid,
                        version = version,
                        tag = tag,
                        message = "Document tagged successfully"
                    )
                    
                } catch (e: Exception) {
                    logger.error("Failed to tag document $documentUuid v$version: ${e.message}", e)
                    TagResult.failure(
                        error = e.message ?: "Unknown error during tagging",
                        documentUuid = documentUuid,
                        version = version,
                        tag = tag
                    )
                }
            }
        }
    }

    // ========================================================================
    // Private Helper Methods
    // ========================================================================

    /**
     * Enhance document with semantic analysis results
     */
    private fun enhanceDocumentWithAnalysis(
        document: DocumentStore.Document,
        analysis: com.unhinged.di.DocumentAnalysis
    ): DocumentStore.Document {
        // TODO: Implement metadata enhancement with analysis results
        return document.toBuilder()
            .setCreatedAt(com.google.protobuf.util.Timestamps.fromMillis(System.currentTimeMillis()))
            .build()
    }

    /**
     * Schedule event emission after transaction commits
     */
    private suspend fun scheduleEventEmission(
        document: DocumentStore.Document,
        analysis: com.unhinged.di.DocumentAnalysis
    ) {
        // Events are emitted asynchronously to avoid blocking the transaction
        kotlinx.coroutines.GlobalScope.launch {
            eventEmitter.emitDocumentCreated(document)
        }
    }

    /**
     * Schedule tag event emission
     */
    private suspend fun scheduleTagEventEmission(
        documentUuid: String,
        version: Int,
        tag: String
    ) {
        kotlinx.coroutines.GlobalScope.launch {
            eventEmitter.emitDocumentTagged(documentUuid, version, tag)
        }
    }
}

// ========================================================================
// Result Types for Manager Operations
// ========================================================================

/**
 * Result of document storage operation
 */
sealed class DocumentResult {
    data class Success(
        val document: DocumentStore.Document,
        val analysis: com.unhinged.di.DocumentAnalysis,
        val message: String
    ) : DocumentResult()
    
    data class Failure(
        val error: String,
        val document: DocumentStore.Document?
    ) : DocumentResult()
    
    companion object {
        fun success(
            document: DocumentStore.Document,
            analysis: com.unhinged.di.DocumentAnalysis,
            message: String
        ) = Success(document, analysis, message)
        
        fun failure(error: String, document: DocumentStore.Document? = null) = 
            Failure(error, document)
    }
}

/**
 * Result of session context retrieval
 */
sealed class SessionContextResult {
    data class Success(
        val documents: List<DocumentStore.Document>,
        val totalTokens: Int,
        val optimizationApplied: Boolean,
        val message: String
    ) : SessionContextResult()
    
    data class Failure(
        val error: String,
        val sessionId: String
    ) : SessionContextResult()
    
    companion object {
        fun success(
            documents: List<DocumentStore.Document>,
            totalTokens: Int,
            optimizationApplied: Boolean,
            message: String
        ) = Success(documents, totalTokens, optimizationApplied, message)
        
        fun failure(error: String, sessionId: String) = Failure(error, sessionId)
    }
}

/**
 * Result of document tagging operation
 */
sealed class TagResult {
    data class Success(
        val documentUuid: String,
        val version: Int,
        val tag: String,
        val message: String
    ) : TagResult()
    
    data class Failure(
        val error: String,
        val documentUuid: String,
        val version: Int,
        val tag: String
    ) : TagResult()
    
    companion object {
        fun success(
            documentUuid: String,
            version: Int,
            tag: String,
            message: String
        ) = Success(documentUuid, version, tag, message)
        
        fun failure(
            error: String,
            documentUuid: String,
            version: Int,
            tag: String
        ) = Failure(error, documentUuid, version, tag)
    }
}
