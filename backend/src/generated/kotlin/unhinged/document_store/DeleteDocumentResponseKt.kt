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

@kotlin.jvm.JvmName("-initializedeleteDocumentResponse")
public inline fun deleteDocumentResponse(block: unhinged.document_store.DeleteDocumentResponseKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.DeleteDocumentResponse =
  unhinged.document_store.DeleteDocumentResponseKt.Dsl._create(unhinged.document_store.DocumentStore.DeleteDocumentResponse.newBuilder()).apply { block() }._build()
/**
 * Protobuf type `unhinged.document_store.DeleteDocumentResponse`
 */
public object DeleteDocumentResponseKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.DeleteDocumentResponse.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.DeleteDocumentResponse.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.DeleteDocumentResponse = _builder.build()

    /**
     * `bool success = 1;`
     */
    public var success: kotlin.Boolean
      @JvmName("getSuccess")
      get() = _builder.getSuccess()
      @JvmName("setSuccess")
      set(value) {
        _builder.setSuccess(value)
      }
    /**
     * `bool success = 1;`
     */
    public fun clearSuccess() {
      _builder.clearSuccess()
    }

    /**
     * `string message = 2;`
     */
    public var message: kotlin.String
      @JvmName("getMessage")
      get() = _builder.getMessage()
      @JvmName("setMessage")
      set(value) {
        _builder.setMessage(value)
      }
    /**
     * `string message = 2;`
     */
    public fun clearMessage() {
      _builder.clearMessage()
    }

    /**
     * `int32 versions_deleted = 3;`
     */
    public var versionsDeleted: kotlin.Int
      @JvmName("getVersionsDeleted")
      get() = _builder.getVersionsDeleted()
      @JvmName("setVersionsDeleted")
      set(value) {
        _builder.setVersionsDeleted(value)
      }
    /**
     * `int32 versions_deleted = 3;`
     */
    public fun clearVersionsDeleted() {
      _builder.clearVersionsDeleted()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.DeleteDocumentResponse.copy(block: `unhinged.document_store`.DeleteDocumentResponseKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.DeleteDocumentResponse =
  `unhinged.document_store`.DeleteDocumentResponseKt.Dsl._create(this.toBuilder()).apply { block() }._build()

