// ============================================================================
// DocumentRepository Interface
// ============================================================================
// 
// Repository interface for document storage operations with PostgreSQL backend
// ============================================================================

package com.unhinged.services.documentstore

import com.google.protobuf.Timestamp
import unhinged.document_store.*

/**
 * Repository interface for document storage operations
 */
interface DocumentRepository {
    
    // ========================================================================
    // Document CRUD Operations
    // ========================================================================
    
    /**
     * Save a document with auto-incrementing version
     */
    suspend fun saveDocument(document: DocumentStore.Document): DocumentStore.Document
    
    /**
     * Get document by UUID and version
     */
    suspend fun getDocumentByVersion(documentUuid: String, version: Int): DocumentStore.Document?
    
    /**
     * Get document by UUID and tag
     */
    suspend fun getDocumentByTag(documentUuid: String, tag: String): DocumentStore.Document?
    
    /**
     * Get latest version of document
     */
    suspend fun getLatestDocument(documentUuid: String): DocumentStore.Document?
    
    /**
     * List documents with filtering and pagination
     */
    suspend fun listDocuments(
        namespace: String? = null,
        type: String? = null,
        tag: String? = null,
        sessionId: String? = null,
        paginationToken: Timestamp? = null,
        pageSize: Int = 50,
        includeBody: Boolean = true,
        latestVersionsOnly: Boolean = false
    ): DocumentListResult
    
    /**
     * List all versions of a specific document
     */
    suspend fun listDocumentVersions(
        documentUuid: String,
        paginationToken: Timestamp? = null,
        pageSize: Int = 50,
        includeBody: Boolean = true
    ): DocumentListResult
    
    /**
     * Get session context documents
     */
    suspend fun getSessionContext(
        sessionId: String,
        documentTypes: List<String>,
        since: Timestamp? = null,
        limit: Int = 100,
        includeBody: Boolean = true
    ): List<DocumentStore.Document>
    
    // ========================================================================
    // Tag Operations
    // ========================================================================
    
    /**
     * Tag a specific document version
     */
    suspend fun tagDocument(
        documentUuid: String,
        version: Int,
        tag: String,
        taggedBy: String,
        taggedByType: String,
        sessionId: String
    )
    
    /**
     * List active tags for a document
     */
    suspend fun listActiveTags(
        documentUuid: String,
        documentVersion: Int? = null,
        paginationToken: Timestamp? = null,
        pageSize: Int = 50
    ): ActiveTagListResult
    
    /**
     * List tag events (audit trail)
     */
    suspend fun listTagEvents(
        documentUuid: String,
        tag: String,
        paginationToken: Timestamp? = null,
        pageSize: Int = 50
    ): TagEventListResult
    
    // ========================================================================
    // Delete Operations
    // ========================================================================
    
    /**
     * Delete a specific document version
     */
    suspend fun deleteDocumentVersion(
        documentUuid: String,
        version: Int,
        deletedBy: String,
        deletedByType: String,
        sessionId: String
    ): Int
    
    /**
     * Delete all versions of a document
     */
    suspend fun deleteAllDocumentVersions(
        documentUuid: String,
        deletedBy: String,
        deletedByType: String,
        sessionId: String
    ): Int
    
    // ========================================================================
    // Health Check
    // ========================================================================
    
    /**
     * Check database connectivity and health
     */
    suspend fun healthCheck(): Boolean
}

// ========================================================================
// Result Data Classes
// ========================================================================

data class DocumentListResult(
    val documents: List<DocumentStore.Document>,
    val totalCount: Int,
    val nextPaginationToken: Timestamp?
)

data class ActiveTagListResult(
    val tags: List<ActiveTag>,
    val totalCount: Int,
    val nextPaginationToken: Timestamp?
)

data class TagEventListResult(
    val events: List<TagEvent>,
    val totalCount: Int,
    val nextPaginationToken: Timestamp?
)
