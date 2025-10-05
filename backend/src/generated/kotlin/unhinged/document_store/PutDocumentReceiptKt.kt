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

@kotlin.jvm.JvmName("-initializeputDocumentReceipt")
public inline fun putDocumentReceipt(block: unhinged.document_store.PutDocumentReceiptKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.PutDocumentReceipt =
  unhinged.document_store.PutDocumentReceiptKt.Dsl._create(unhinged.document_store.DocumentStore.PutDocumentReceipt.newBuilder()).apply { block() }._build()
/**
 * Protobuf type `unhinged.document_store.PutDocumentReceipt`
 */
public object PutDocumentReceiptKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.PutDocumentReceipt.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.PutDocumentReceipt.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.PutDocumentReceipt = _builder.build()

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
     * `int32 version = 2;`
     */
    public var version: kotlin.Int
      @JvmName("getVersion")
      get() = _builder.getVersion()
      @JvmName("setVersion")
      set(value) {
        _builder.setVersion(value)
      }
    /**
     * `int32 version = 2;`
     */
    public fun clearVersion() {
      _builder.clearVersion()
    }

    /**
     * `bool success = 3;`
     */
    public var success: kotlin.Boolean
      @JvmName("getSuccess")
      get() = _builder.getSuccess()
      @JvmName("setSuccess")
      set(value) {
        _builder.setSuccess(value)
      }
    /**
     * `bool success = 3;`
     */
    public fun clearSuccess() {
      _builder.clearSuccess()
    }

    /**
     * `string error_message = 4;`
     */
    public var errorMessage: kotlin.String
      @JvmName("getErrorMessage")
      get() = _builder.getErrorMessage()
      @JvmName("setErrorMessage")
      set(value) {
        _builder.setErrorMessage(value)
      }
    /**
     * `string error_message = 4;`
     */
    public fun clearErrorMessage() {
      _builder.clearErrorMessage()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.PutDocumentReceipt.copy(block: `unhinged.document_store`.PutDocumentReceiptKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.PutDocumentReceipt =
  `unhinged.document_store`.PutDocumentReceiptKt.Dsl._create(this.toBuilder()).apply { block() }._build()

