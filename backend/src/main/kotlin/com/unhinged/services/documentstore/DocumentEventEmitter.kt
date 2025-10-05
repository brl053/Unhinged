// ============================================================================
// DocumentEventEmitter Interface
// ============================================================================
// 
// Event emission interface for document operations to integrate with CDC system
// ============================================================================

package com.unhinged.services.documentstore

import unhinged.document_store.DocumentStore

/**
 * Interface for emitting document-related events for CDC and workflow triggers
 */
interface DocumentEventEmitter {
    
    /**
     * Emit event when a document is created or updated
     */
    suspend fun emitDocumentCreated(document: DocumentStore.Document)
    
    /**
     * Emit event when a document is accessed/retrieved
     */
    suspend fun emitDocumentAccessed(document: DocumentStore.Document)
    
    /**
     * Emit event when a document is tagged
     */
    suspend fun emitDocumentTagged(documentUuid: String, version: Int, tag: String)
    
    /**
     * Emit event when a document is deleted
     */
    suspend fun emitDocumentDeleted(documentUuid: String, versionsDeleted: Int)
    
    /**
     * Emit event when session context is accessed
     */
    suspend fun emitSessionContextAccessed(sessionId: String, documentCount: Int)
}
