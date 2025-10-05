// ============================================================================
// GENERATED FILE - DO NOT EDIT
// ============================================================================
// Proto Version: 1.1.0
// Proto Hash: 428cdba09611d53032ca330a1bf39a453e727421425de962303fd66a5084f283
// Build: 2025.01.04.001
// Generated: 2025-10-05T05:39:54Z
// 
// This file was automatically generated from protobuf schemas.
// To regenerate: npm run build:proto
// 
// Version validation: If proto hash changes, regenerate this file.
// ============================================================================

// source: document_store.proto

// Generated files should ignore deprecation warnings
@file:Suppress("DEPRECATION")
package unhinged.document_store;

@kotlin.jvm.JvmName("-initializedeleteDocumentRequest")
public inline fun deleteDocumentRequest(block: unhinged.document_store.DeleteDocumentRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.DeleteDocumentRequest =
  unhinged.document_store.DeleteDocumentRequestKt.Dsl._create(unhinged.document_store.DocumentStore.DeleteDocumentRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * Delete operations
 * ```
 *
 * Protobuf type `unhinged.document_store.DeleteDocumentRequest`
 */
public object DeleteDocumentRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.DeleteDocumentRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.DeleteDocumentRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.DeleteDocumentRequest = _builder.build()

    /**
     * `string document_uuid = 1;`
     */
    public var documentUuid: kotlin.String
      @JvmName("getDocumentUuid")
      get() = _builder.getDocumentUuid()
      @JvmName("setDocumentUuid")
      set(value) {
        _builder.setDocumentUuid(value)
      }
    /**
     * `string document_uuid = 1;`
     */
    public fun clearDocumentUuid() {
      _builder.clearDocumentUuid()
    }

    /**
     * ```
     * If not specified, deletes all versions
     * ```
     *
     * `optional int32 version = 2;`
     */
    public var version: kotlin.Int
      @JvmName("getVersion")
      get() = _builder.getVersion()
      @JvmName("setVersion")
      set(value) {
        _builder.setVersion(value)
      }
    /**
     * ```
     * If not specified, deletes all versions
     * ```
     *
     * `optional int32 version = 2;`
     */
    public fun clearVersion() {
      _builder.clearVersion()
    }
    /**
     * ```
     * If not specified, deletes all versions
     * ```
     *
     * `optional int32 version = 2;`
     * @return Whether the version field is set.
     */
    public fun hasVersion(): kotlin.Boolean {
      return _builder.hasVersion()
    }

    /**
     * `string deleted_by = 3;`
     */
    public var deletedBy: kotlin.String
      @JvmName("getDeletedBy")
      get() = _builder.getDeletedBy()
      @JvmName("setDeletedBy")
      set(value) {
        _builder.setDeletedBy(value)
      }
    /**
     * `string deleted_by = 3;`
     */
    public fun clearDeletedBy() {
      _builder.clearDeletedBy()
    }

    /**
     * `string deleted_by_type = 4;`
     */
    public var deletedByType: kotlin.String
      @JvmName("getDeletedByType")
      get() = _builder.getDeletedByType()
      @JvmName("setDeletedByType")
      set(value) {
        _builder.setDeletedByType(value)
      }
    /**
     * `string deleted_by_type = 4;`
     */
    public fun clearDeletedByType() {
      _builder.clearDeletedByType()
    }

    /**
     * `string session_id = 5;`
     */
    public var sessionId: kotlin.String
      @JvmName("getSessionId")
      get() = _builder.getSessionId()
      @JvmName("setSessionId")
      set(value) {
        _builder.setSessionId(value)
      }
    /**
     * `string session_id = 5;`
     */
    public fun clearSessionId() {
      _builder.clearSessionId()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.DeleteDocumentRequest.copy(block: `unhinged.document_store`.DeleteDocumentRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.DeleteDocumentRequest =
  `unhinged.document_store`.DeleteDocumentRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

