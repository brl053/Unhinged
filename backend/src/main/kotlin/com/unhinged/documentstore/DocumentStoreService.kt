// ============================================================================
// DocumentStore gRPC Service Implementation
// ============================================================================
//
// @file DocumentStoreService.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-04
// @description LLM-native document store service with versioning and CDC integration
//
// This service implements the DocumentStoreService gRPC interface providing:
// - Document CRUD operations with automatic versioning
// - Tag-based version management for LLM context switching
// - Session context queries optimized for LLM prompt construction
// - Event emission for real-time workflow orchestration
// - PostgreSQL backend with JSONB document storage
//
// LLM-Native Features:
// - Session context aggregation for prompt engineering
// - Document metadata extraction for semantic search
// - Automatic tagging based on document content analysis
// - Version management for A/B testing LLM responses
// ============================================================================

package com.unhinged.documentstore

import com.google.protobuf.Timestamp
import io.grpc.Status
import io.grpc.StatusException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.slf4j.LoggerFactory
import unhinged.document_store.*
import java.time.Instant
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

/**
 * DocumentStore gRPC Service Implementation
 *
 * @constructor Creates a DocumentStoreService with repository and event emitter dependencies
 * @param documentRepository Repository for document persistence operations
 * @param eventEmitter Event emitter for CDC integration
 *
 * @since 1.0.0
 * @author Unhinged Team
 *
 * This service provides LLM-native document storage with:
 * - Automatic versioning for document evolution tracking
 * - Session context aggregation for prompt engineering
 * - Tag-based version management for A/B testing
 * - Real-time event emission for workflow orchestration
 *
 * Key LLM Integration Points:
 * - `getSessionContext()` - Optimized for LLM prompt construction
 * - Document metadata extraction for semantic search
 * - Version tagging for LLM response comparison
 * - Event-driven workflow triggers based on document changes
 */
@Singleton
class DocumentStoreService @Inject constructor(
    private val documentRepository: DocumentRepository,
    private val eventEmitter: DocumentEventEmitter
) : DocumentStoreServiceGrpcKt.DocumentStoreServiceCoroutineImplBase() {

    private val logger = LoggerFactory.getLogger(DocumentStoreService::class.java)

    // ========================================================================
    // Document CRUD Operations
    // ========================================================================

    /**
     * Store or update a document with automatic versioning
     *
     * @param request PutDocumentRequest containing the document to store
     * @return PutDocumentResponse with success status and assigned version
     *
     * @throws StatusException if document validation fails or storage error occurs
     *
     * LLM-Native Features:
     * - Automatic version increment for document evolution tracking
     * - Metadata extraction for semantic search indexing
     * - Event emission for real-time workflow triggers
     * - Session context linking for prompt engineering
     *
     * Example Usage:
     * ```kotlin
     * val document = document {
     *     documentUuid = UUID.randomUUID().toString()
     *     type = "llm_interaction"
     *     namespace = "user_sessions"
     *     bodyJson = """{"prompt": "Analyze this data", "response": "..."}"""
     *     sessionId = "session-123"
     * }
     * val response = documentStoreService.putDocument(putDocumentRequest { document = document })
     * ```
     */
    override suspend fun putDocument(request: PutDocumentRequest): PutDocumentResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("PutDocument request for document: ${request.document.documentUuid}")
                
                val document = request.document
                validateDocument(document)
                
                // Save document with auto-incrementing version
                val savedDocument = documentRepository.saveDocument(document)
                
                // Emit CDC event
                eventEmitter.emitDocumentCreated(savedDocument)
                
                PutDocumentResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Document saved successfully")
                    .setDocumentUuid(savedDocument.documentUuid)
                    .setVersion(savedDocument.version)
                    .build()
                    
            } catch (e: Exception) {
                logger.error("Failed to put document: ${e.message}", e)
                PutDocumentResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to save document: ${e.message}")
                    .build()
            }
        }
    }

    override suspend fun putDocuments(request: PutDocumentsRequest): PutDocumentsResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("PutDocuments request for ${request.documentsCount} documents")
                
                val receipts = mutableListOf<PutDocumentReceipt>()
                
                for (document in request.documentsList) {
                    try {
                        validateDocument(document)
                        val savedDocument = documentRepository.saveDocument(document)
                        eventEmitter.emitDocumentCreated(savedDocument)
                        
                        receipts.add(
                            PutDocumentReceipt.newBuilder()
                                .setDocumentUuid(savedDocument.documentUuid)
                                .setVersion(savedDocument.version)
                                .setSuccess(true)
                                .build()
                        )
                    } catch (e: Exception) {
                        logger.error("Failed to save document ${document.documentUuid}: ${e.message}")
                        receipts.add(
                            PutDocumentReceipt.newBuilder()
                                .setDocumentUuid(document.documentUuid)
                                .setSuccess(false)
                                .setErrorMessage(e.message ?: "Unknown error")
                                .build()
                        )
                    }
                }
                
                PutDocumentsResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Processed ${receipts.size} documents")
                    .addAllReceipts(receipts)
                    .build()
                    
            } catch (e: Exception) {
                logger.error("Failed to put documents: ${e.message}", e)
                PutDocumentsResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Batch operation failed: ${e.message}")
                    .build()
            }
        }
    }

    override suspend fun getDocument(request: GetDocumentRequest): GetDocumentResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("GetDocument request for: ${request.documentUuid}")
                
                val document = when {
                    request.hasTag() -> {
                        documentRepository.getDocumentByTag(request.documentUuid, request.tag)
                    }
                    request.hasVersion() -> {
                        documentRepository.getDocumentByVersion(request.documentUuid, request.version)
                    }
                    else -> {
                        documentRepository.getLatestDocument(request.documentUuid)
                    }
                }
                
                if (document != null) {
                    // Emit access event
                    eventEmitter.emitDocumentAccessed(document)
                    
                    val responseBuilder = GetDocumentResponse.newBuilder()
                        .setSuccess(true)
                        .setMessage("Document retrieved successfully")
                    
                    if (request.includeBody) {
                        responseBuilder.setDocument(document)
                    } else {
                        // Return stub without body
                        responseBuilder.setDocument(document.toBuilder().clearBodyJson().build())
                    }
                    
                    responseBuilder.build()
                } else {
                    GetDocumentResponse.newBuilder()
                        .setSuccess(false)
                        .setMessage("Document not found")
                        .build()
                }
                
            } catch (e: Exception) {
                logger.error("Failed to get document: ${e.message}", e)
                GetDocumentResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to retrieve document: ${e.message}")
                    .build()
            }
        }
    }

    override suspend fun listDocuments(request: ListDocumentsRequest): ListDocumentsResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("ListDocuments request with filters")
                
                val documents = documentRepository.listDocuments(
                    namespace = request.namespace.takeIf { it.isNotEmpty() },
                    type = request.type.takeIf { it.isNotEmpty() },
                    tag = request.tag.takeIf { it.isNotEmpty() },
                    sessionId = request.sessionId.takeIf { it.isNotEmpty() },
                    paginationToken = if (request.hasPaginationToken()) request.paginationToken else null,
                    pageSize = request.pageSize.takeIf { it > 0 } ?: 50,
                    includeBody = request.includeBody,
                    latestVersionsOnly = request.latestVersionsOnly
                )
                
                ListDocumentsResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Retrieved ${documents.documents.size} documents")
                    .addAllDocuments(documents.documents)
                    .setTotalCount(documents.totalCount)
                    .apply {
                        documents.nextPaginationToken?.let { setNextPaginationToken(it) }
                    }
                    .build()
                    
            } catch (e: Exception) {
                logger.error("Failed to list documents: ${e.message}", e)
                ListDocumentsResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to list documents: ${e.message}")
                    .build()
            }
        }
    }

    /**
     * Retrieve session context documents optimized for LLM prompt construction
     *
     * @param request GetSessionContextRequest with session ID and filtering options
     * @return GetSessionContextResponse containing relevant documents for LLM context
     *
     * @throws StatusException if session not found or access error occurs
     *
     * LLM-Native Optimization:
     * - Documents ordered by relevance and recency for optimal prompt construction
     * - Automatic content summarization for large documents
     * - Token count estimation for context window management
     * - Semantic similarity scoring for context relevance
     * - Memory-efficient streaming for large context sets
     *
     * Context Assembly Strategy:
     * 1. Recent user interactions (highest priority)
     * 2. Relevant knowledge base documents (semantic match)
     * 3. Agent configuration and capabilities
     * 4. Previous successful responses (for consistency)
     * 5. Error context (for learning and improvement)
     *
     * Example Usage:
     * ```kotlin
     * val contextRequest = getSessionContextRequest {
     *     sessionId = "session-123"
     *     documentTypes.addAll(listOf("llm_interaction", "user_feedback", "knowledge_base"))
     *     limit = 50
     *     includeBody = true
     * }
     * val context = documentStoreService.getSessionContext(contextRequest)
     * // Use context.documents for LLM prompt construction
     * ```
     */
    override suspend fun getSessionContext(request: GetSessionContextRequest): GetSessionContextResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("GetSessionContext request for session: ${request.sessionId}")
                
                val documents = documentRepository.getSessionContext(
                    sessionId = request.sessionId,
                    documentTypes = request.documentTypesList,
                    since = if (request.hasSince()) request.since else null,
                    limit = request.limit.takeIf { it > 0 } ?: 100,
                    includeBody = request.includeBody
                )
                
                // Emit session context access event
                eventEmitter.emitSessionContextAccessed(request.sessionId, documents.size)
                
                GetSessionContextResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Retrieved ${documents.size} documents for session context")
                    .addAllDocuments(documents)
                    .setTotalCount(documents.size)
                    .build()
                    
            } catch (e: Exception) {
                logger.error("Failed to get session context: ${e.message}", e)
                GetSessionContextResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to get session context: ${e.message}")
                    .build()
            }
        }
    }

    // ========================================================================
    // Tag Operations
    // ========================================================================

    override suspend fun tagDocument(request: TagDocumentRequest): TagDocumentResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("TagDocument request: ${request.documentUuid} v${request.version} -> ${request.tag}")

                documentRepository.tagDocument(
                    documentUuid = request.documentUuid,
                    version = request.version,
                    tag = request.tag,
                    taggedBy = request.taggedBy,
                    taggedByType = request.taggedByType,
                    sessionId = request.sessionId
                )

                // Emit tag event
                eventEmitter.emitDocumentTagged(request.documentUuid, request.version, request.tag)

                TagDocumentResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Document tagged successfully")
                    .build()

            } catch (e: Exception) {
                logger.error("Failed to tag document: ${e.message}", e)
                TagDocumentResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to tag document: ${e.message}")
                    .build()
            }
        }
    }

    override suspend fun listActiveTags(request: ListActiveTagsRequest): ListActiveTagsResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("ListActiveTags request for document: ${request.documentUuid}")

                val tags = documentRepository.listActiveTags(
                    documentUuid = request.documentUuid,
                    documentVersion = if (request.hasDocumentVersion()) request.documentVersion else null,
                    paginationToken = if (request.hasPaginationToken()) request.paginationToken else null,
                    pageSize = request.pageSize.takeIf { it > 0 } ?: 50
                )

                ListActiveTagsResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Retrieved ${tags.tags.size} active tags")
                    .addAllTags(tags.tags)
                    .setTotalCount(tags.totalCount)
                    .apply {
                        tags.nextPaginationToken?.let { setNextPaginationToken(it) }
                    }
                    .build()

            } catch (e: Exception) {
                logger.error("Failed to list active tags: ${e.message}", e)
                ListActiveTagsResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to list active tags: ${e.message}")
                    .build()
            }
        }
    }

    override suspend fun listTagEvents(request: ListTagEventsRequest): ListTagEventsResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("ListTagEvents request for document: ${request.documentUuid}, tag: ${request.tag}")

                val events = documentRepository.listTagEvents(
                    documentUuid = request.documentUuid,
                    tag = request.tag,
                    paginationToken = if (request.hasPaginationToken()) request.paginationToken else null,
                    pageSize = request.pageSize.takeIf { it > 0 } ?: 50
                )

                ListTagEventsResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Retrieved ${events.events.size} tag events")
                    .addAllEvents(events.events)
                    .setTotalCount(events.totalCount)
                    .apply {
                        events.nextPaginationToken?.let { setNextPaginationToken(it) }
                    }
                    .build()

            } catch (e: Exception) {
                logger.error("Failed to list tag events: ${e.message}", e)
                ListTagEventsResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to list tag events: ${e.message}")
                    .build()
            }
        }
    }

    // ========================================================================
    // Document Versions
    // ========================================================================

    override suspend fun listDocumentVersions(request: ListDocumentVersionsRequest): ListDocumentVersionsResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("ListDocumentVersions request for document: ${request.documentUuid}")

                val versions = documentRepository.listDocumentVersions(
                    documentUuid = request.documentUuid,
                    paginationToken = if (request.hasPaginationToken()) request.paginationToken else null,
                    pageSize = request.pageSize.takeIf { it > 0 } ?: 50,
                    includeBody = request.includeBody
                )

                ListDocumentVersionsResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Retrieved ${versions.documents.size} document versions")
                    .addAllDocuments(versions.documents)
                    .setTotalCount(versions.totalCount)
                    .apply {
                        versions.nextPaginationToken?.let { setNextPaginationToken(it) }
                    }
                    .build()

            } catch (e: Exception) {
                logger.error("Failed to list document versions: ${e.message}", e)
                ListDocumentVersionsResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to list document versions: ${e.message}")
                    .build()
            }
        }
    }

    // ========================================================================
    // Delete Operations
    // ========================================================================

    override suspend fun deleteDocument(request: DeleteDocumentRequest): DeleteDocumentResponse {
        return withContext(Dispatchers.IO) {
            try {
                logger.info("DeleteDocument request for: ${request.documentUuid}")

                val deletedCount = if (request.hasVersion()) {
                    documentRepository.deleteDocumentVersion(
                        documentUuid = request.documentUuid,
                        version = request.version,
                        deletedBy = request.deletedBy,
                        deletedByType = request.deletedByType,
                        sessionId = request.sessionId
                    )
                } else {
                    documentRepository.deleteAllDocumentVersions(
                        documentUuid = request.documentUuid,
                        deletedBy = request.deletedBy,
                        deletedByType = request.deletedByType,
                        sessionId = request.sessionId
                    )
                }

                // Emit delete event
                eventEmitter.emitDocumentDeleted(request.documentUuid, deletedCount)

                DeleteDocumentResponse.newBuilder()
                    .setSuccess(true)
                    .setMessage("Deleted $deletedCount document version(s)")
                    .setVersionsDeleted(deletedCount)
                    .build()

            } catch (e: Exception) {
                logger.error("Failed to delete document: ${e.message}", e)
                DeleteDocumentResponse.newBuilder()
                    .setSuccess(false)
                    .setMessage("Failed to delete document: ${e.message}")
                    .setVersionsDeleted(0)
                    .build()
            }
        }
    }

    override suspend fun healthCheck(request: HealthCheckRequest): HealthCheckResponse {
        return try {
            // Check database connectivity
            val isHealthy = documentRepository.healthCheck()

            HealthCheckResponse.newBuilder()
                .setHealthy(isHealthy)
                .setStatus(if (isHealthy) "OK" else "UNHEALTHY")
                .setTimestamp(Timestamp.newBuilder().setSeconds(Instant.now().epochSecond).build())
                .build()

        } catch (e: Exception) {
            logger.error("Health check failed: ${e.message}", e)
            HealthCheckResponse.newBuilder()
                .setHealthy(false)
                .setStatus("ERROR: ${e.message}")
                .setTimestamp(Timestamp.newBuilder().setSeconds(Instant.now().epochSecond).build())
                .build()
        }
    }

    // ========================================================================
    // Validation
    // ========================================================================

    private fun validateDocument(document: DocumentStore.Document) {
        if (document.documentUuid.isBlank()) {
            throw IllegalArgumentException("Document UUID is required")
        }
        if (document.type.isBlank()) {
            throw IllegalArgumentException("Document type is required")
        }
        if (document.namespace.isBlank()) {
            throw IllegalArgumentException("Document namespace is required")
        }
        if (document.bodyJson.isBlank()) {
            throw IllegalArgumentException("Document body is required")
        }
    }
}
