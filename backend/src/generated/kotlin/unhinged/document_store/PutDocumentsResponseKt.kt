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

@kotlin.jvm.JvmName("-initializeputDocumentsResponse")
public inline fun putDocumentsResponse(block: unhinged.document_store.PutDocumentsResponseKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.PutDocumentsResponse =
  unhinged.document_store.PutDocumentsResponseKt.Dsl._create(unhinged.document_store.DocumentStore.PutDocumentsResponse.newBuilder()).apply { block() }._build()
/**
 * Protobuf type `unhinged.document_store.PutDocumentsResponse`
 */
public object PutDocumentsResponseKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.PutDocumentsResponse.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.PutDocumentsResponse.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.PutDocumentsResponse = _builder.build()

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
     * An uninstantiable, behaviorless type to represent the field in
     * generics.
     */
    @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
    public class ReceiptsProxy private constructor() : com.google.protobuf.kotlin.DslProxy()
    /**
     * `repeated .unhinged.document_store.PutDocumentReceipt receipts = 3;`
     */
     public val receipts: com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.PutDocumentReceipt, ReceiptsProxy>
      @kotlin.jvm.JvmSynthetic
      get() = com.google.protobuf.kotlin.DslList(
        _builder.getReceiptsList()
      )
    /**
     * `repeated .unhinged.document_store.PutDocumentReceipt receipts = 3;`
     * @param value The receipts to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addReceipts")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.PutDocumentReceipt, ReceiptsProxy>.add(value: unhinged.document_store.DocumentStore.PutDocumentReceipt) {
      _builder.addReceipts(value)
    }
    /**
     * `repeated .unhinged.document_store.PutDocumentReceipt receipts = 3;`
     * @param value The receipts to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignReceipts")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.PutDocumentReceipt, ReceiptsProxy>.plusAssign(value: unhinged.document_store.DocumentStore.PutDocumentReceipt) {
      add(value)
    }
    /**
     * `repeated .unhinged.document_store.PutDocumentReceipt receipts = 3;`
     * @param values The receipts to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addAllReceipts")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.PutDocumentReceipt, ReceiptsProxy>.addAll(values: kotlin.collections.Iterable<unhinged.document_store.DocumentStore.PutDocumentReceipt>) {
      _builder.addAllReceipts(values)
    }
    /**
     * `repeated .unhinged.document_store.PutDocumentReceipt receipts = 3;`
     * @param values The receipts to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignAllReceipts")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.PutDocumentReceipt, ReceiptsProxy>.plusAssign(values: kotlin.collections.Iterable<unhinged.document_store.DocumentStore.PutDocumentReceipt>) {
      addAll(values)
    }
    /**
     * `repeated .unhinged.document_store.PutDocumentReceipt receipts = 3;`
     * @param index The index to set the value at.
     * @param value The receipts to set.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("setReceipts")
    public operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.PutDocumentReceipt, ReceiptsProxy>.set(index: kotlin.Int, value: unhinged.document_store.DocumentStore.PutDocumentReceipt) {
      _builder.setReceipts(index, value)
    }
    /**
     * `repeated .unhinged.document_store.PutDocumentReceipt receipts = 3;`
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("clearReceipts")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.PutDocumentReceipt, ReceiptsProxy>.clear() {
      _builder.clearReceipts()
    }

  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.PutDocumentsResponse.copy(block: `unhinged.document_store`.PutDocumentsResponseKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.PutDocumentsResponse =
  `unhinged.document_store`.PutDocumentsResponseKt.Dsl._create(this.toBuilder()).apply { block() }._build()

