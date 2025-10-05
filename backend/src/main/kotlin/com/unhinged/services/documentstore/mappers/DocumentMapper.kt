// ============================================================================
// Document Mapper - Clean Boundary Between Protobuf and Domain
// ============================================================================
// 
// @file DocumentMapper.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-04
// @description Mappers for translating between gRPC protobuf and domain models
// 
// This mapper maintains clean separation between:
// - Transport layer (gRPC protobuf messages)
// - Domain layer (pure business models)
// - Infrastructure layer (database entities)
// 
// Following Clean Architecture principles:
// - Domain models have no framework dependencies
// - Protobuf types stay at service boundaries
// - Mapping logic is isolated and testable
// ============================================================================

package com.unhinged.services.documentstore.mappers

import com.google.protobuf.util.Timestamps
import org.slf4j.LoggerFactory
import unhinged.document_store.*
import java.time.Instant

/**
 * Mapper for Document entities between protobuf and domain models
 * 
 * Handles bidirectional mapping while keeping domain models clean
 * of protobuf annotations and transport concerns.
 * 
 * @since 1.0.0
 * @author Unhinged Team
 */
object DocumentMapper {
    
    private val logger = LoggerFactory.getLogger(DocumentMapper::class.java)

    // ========================================================================
    // Domain Model (Clean, No Framework Dependencies)
    // ========================================================================

    /**
     * Pure domain model for Document
     * 
     * This represents our business concept of a document without
     * any transport protocol or persistence framework concerns.
     */
    data class Document(
        val id: String,
        val type: String,
        val name: String,
        val namespace: String,
        val version: Int,
        val content: String,
        val metadata: Map<String, String>,
        val tags: List<String>,
        val createdAt: Instant,
        val createdBy: String,
        val createdByType: String,
        val sessionId: String
    ) {
        /**
         * Business logic methods can be added here
         */
        fun isLLMInteraction(): Boolean = type == "llm_interaction"
        fun isUserFeedback(): Boolean = type == "user_feedback"
        fun hasSession(): Boolean = sessionId.isNotBlank()
        
        /**
         * Estimate token count for LLM context management
         */
        fun estimateTokenCount(): Int = (content.length / 4).coerceAtLeast(1)
        
        /**
         * Check if document is suitable for LLM context
         */
        fun isSuitableForContext(maxTokens: Int): Boolean {
            return estimateTokenCount() <= maxTokens && content.isNotBlank()
        }
    }

    // ========================================================================
    // Protobuf to Domain Mapping
    // ========================================================================

    /**
     * Convert protobuf Document to domain Document
     * 
     * @param proto Protobuf document from gRPC request
     * @return Clean domain model
     */
    fun toDomain(proto: DocumentStore.Document): Document {
        return try {
            Document(
                id = proto.documentUuid,
                type = proto.type,
                name = proto.name,
                namespace = proto.namespace,
                version = proto.version,
                content = proto.bodyJson,
                metadata = extractMetadataMap(proto),
                tags = proto.tagsList.toList(),
                createdAt = if (proto.hasCreatedAt()) {
                    Instant.ofEpochSecond(
                        proto.createdAt.seconds,
                        proto.createdAt.nanos.toLong()
                    )
                } else {
                    Instant.now()
                },
                createdBy = proto.createdBy,
                createdByType = proto.createdByType,
                sessionId = proto.sessionId
            )
        } catch (e: Exception) {
            logger.error("Failed to map protobuf to domain: ${e.message}", e)
            throw IllegalArgumentException("Invalid protobuf document: ${e.message}", e)
        }
    }

    /**
     * Convert domain Document to protobuf Document
     * 
     * @param domain Clean domain model
     * @return Protobuf document for gRPC response
     */
    fun toProto(domain: Document): DocumentStore.Document {
        return try {
            DocumentStore.Document.newBuilder()
                .setDocumentUuid(domain.id)
                .setType(domain.type)
                .setName(domain.name)
                .setNamespace(domain.namespace)
                .setVersion(domain.version)
                .setBodyJson(domain.content)
                .setCreatedAt(Timestamps.fromMillis(domain.createdAt.toEpochMilli()))
                .setCreatedBy(domain.createdBy)
                .setCreatedByType(domain.createdByType)
                .setSessionId(domain.sessionId)
                .addAllTags(domain.tags)
                .build()
        } catch (e: Exception) {
            logger.error("Failed to map domain to protobuf: ${e.message}", e)
            throw IllegalArgumentException("Invalid domain document: ${e.message}", e)
        }
    }

    // ========================================================================
    // Request/Response Mapping
    // ========================================================================

    /**
     * Extract document from PutDocumentRequest
     */
    fun fromPutRequest(request: PutDocumentRequest): Document {
        if (!request.hasDocument()) {
            throw IllegalArgumentException("PutDocumentRequest must contain a document")
        }
        return toDomain(request.document)
    }

    /**
     * Create PutDocumentResponse from domain result
     */
    fun toPutResponse(
        success: Boolean,
        message: String,
        document: Document? = null,
        version: Int = 0
    ): PutDocumentResponse {
        return PutDocumentResponse.newBuilder()
            .setSuccess(success)
            .setMessage(message)
            .setVersion(version)
            .apply {
                if (document != null) {
                    setDocument(toProto(document))
                }
            }
            .build()
    }

    /**
     * Create GetDocumentResponse from domain document
     */
    fun toGetResponse(
        success: Boolean,
        message: String,
        document: Document? = null
    ): GetDocumentResponse {
        return GetDocumentResponse.newBuilder()
            .setSuccess(success)
            .setMessage(message)
            .apply {
                if (document != null) {
                    setDocument(toProto(document))
                }
            }
            .build()
    }

    /**
     * Create GetSessionContextResponse from domain documents
     */
    fun toSessionContextResponse(
        success: Boolean,
        message: String,
        documents: List<Document> = emptyList(),
        totalTokens: Int = 0,
        optimizationApplied: Boolean = false
    ): GetSessionContextResponse {
        return GetSessionContextResponse.newBuilder()
            .setSuccess(success)
            .setMessage(message)
            .addAllDocuments(documents.map { toProto(it) })
            .putMetadata("total_tokens", totalTokens.toString())
            .putMetadata("optimization_applied", optimizationApplied.toString())
            .putMetadata("document_count", documents.size.toString())
            .build()
    }

    /**
     * Create TagDocumentResponse from operation result
     */
    fun toTagResponse(
        success: Boolean,
        message: String,
        documentUuid: String = "",
        version: Int = 0,
        tag: String = ""
    ): TagDocumentResponse {
        return TagDocumentResponse.newBuilder()
            .setSuccess(success)
            .setMessage(message)
            .putMetadata("document_uuid", documentUuid)
            .putMetadata("version", version.toString())
            .putMetadata("tag", tag)
            .build()
    }

    // ========================================================================
    // Helper Methods
    // ========================================================================

    /**
     * Extract metadata map from protobuf document
     * 
     * Handles the protobuf Struct -> Map conversion safely
     */
    private fun extractMetadataMap(proto: DocumentStore.Document): Map<String, String> {
        return try {
            if (proto.hasMetadata()) {
                // TODO: Implement proper Struct to Map conversion
                // For now, return empty map
                emptyMap()
            } else {
                emptyMap()
            }
        } catch (e: Exception) {
            logger.warn("Failed to extract metadata from protobuf: ${e.message}")
            emptyMap()
        }
    }

    /**
     * Convert Map to protobuf Struct
     * 
     * Handles the Map -> protobuf Struct conversion safely
     */
    private fun mapToStruct(metadata: Map<String, String>): com.google.protobuf.Struct {
        // TODO: Implement proper Map to Struct conversion
        return com.google.protobuf.Struct.getDefaultInstance()
    }

    // ========================================================================
    // Validation Helpers
    // ========================================================================

    /**
     * Validate domain document before mapping
     */
    fun validateDomain(document: Document): List<String> {
        val errors = mutableListOf<String>()
        
        if (document.id.isBlank()) {
            errors.add("Document ID cannot be blank")
        }
        
        if (document.type.isBlank()) {
            errors.add("Document type cannot be blank")
        }
        
        if (document.namespace.isBlank()) {
            errors.add("Document namespace cannot be blank")
        }
        
        if (document.version < 1) {
            errors.add("Document version must be positive")
        }
        
        if (document.content.isBlank()) {
            errors.add("Document content cannot be blank")
        }
        
        return errors
    }

    /**
     * Validate protobuf document before mapping
     */
    fun validateProto(proto: DocumentStore.Document): List<String> {
        val errors = mutableListOf<String>()
        
        if (proto.documentUuid.isBlank()) {
            errors.add("Document UUID cannot be blank")
        }
        
        if (proto.type.isBlank()) {
            errors.add("Document type cannot be blank")
        }
        
        if (proto.namespace.isBlank()) {
            errors.add("Document namespace cannot be blank")
        }
        
        if (proto.bodyJson.isBlank()) {
            errors.add("Document body cannot be blank")
        }
        
        return errors
    }
}

// ========================================================================
// Extension Functions for Convenience
// ========================================================================

/**
 * Extension function to convert protobuf document to domain
 */
fun DocumentStore.Document.toDomain(): DocumentMapper.Document = DocumentMapper.toDomain(this)

/**
 * Extension function to convert domain document to protobuf
 */
fun DocumentMapper.Document.toProto(): DocumentStore.Document = DocumentMapper.toProto(this)

/**
 * Extension function to validate domain document
 */
fun DocumentMapper.Document.validate(): List<String> = DocumentMapper.validateDomain(this)

/**
 * Extension function to check if domain document is valid
 */
fun DocumentMapper.Document.isValid(): Boolean = validate().isEmpty()
