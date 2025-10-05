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

@kotlin.jvm.JvmName("-initializeputDocumentsRequest")
public inline fun putDocumentsRequest(block: unhinged.document_store.PutDocumentsRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.PutDocumentsRequest =
  unhinged.document_store.PutDocumentsRequestKt.Dsl._create(unhinged.document_store.DocumentStore.PutDocumentsRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * Batch create/update documents
 * ```
 *
 * Protobuf type `unhinged.document_store.PutDocumentsRequest`
 */
public object PutDocumentsRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.PutDocumentsRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.PutDocumentsRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.PutDocumentsRequest = _builder.build()

    /**
     * An uninstantiable, behaviorless type to represent the field in
     * generics.
     */
    @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
    public class DocumentsProxy private constructor() : com.google.protobuf.kotlin.DslProxy()
    /**
     * `repeated .unhinged.document_store.Document documents = 1;`
     */
     public val documents: com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.Document, DocumentsProxy>
      @kotlin.jvm.JvmSynthetic
      get() = com.google.protobuf.kotlin.DslList(
        _builder.getDocumentsList()
      )
    /**
     * `repeated .unhinged.document_store.Document documents = 1;`
     * @param value The documents to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addDocuments")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.Document, DocumentsProxy>.add(value: unhinged.document_store.DocumentStore.Document) {
      _builder.addDocuments(value)
    }
    /**
     * `repeated .unhinged.document_store.Document documents = 1;`
     * @param value The documents to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignDocuments")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.Document, DocumentsProxy>.plusAssign(value: unhinged.document_store.DocumentStore.Document) {
      add(value)
    }
    /**
     * `repeated .unhinged.document_store.Document documents = 1;`
     * @param values The documents to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addAllDocuments")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.Document, DocumentsProxy>.addAll(values: kotlin.collections.Iterable<unhinged.document_store.DocumentStore.Document>) {
      _builder.addAllDocuments(values)
    }
    /**
     * `repeated .unhinged.document_store.Document documents = 1;`
     * @param values The documents to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignAllDocuments")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.Document, DocumentsProxy>.plusAssign(values: kotlin.collections.Iterable<unhinged.document_store.DocumentStore.Document>) {
      addAll(values)
    }
    /**
     * `repeated .unhinged.document_store.Document documents = 1;`
     * @param index The index to set the value at.
     * @param value The documents to set.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("setDocuments")
    public operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.Document, DocumentsProxy>.set(index: kotlin.Int, value: unhinged.document_store.DocumentStore.Document) {
      _builder.setDocuments(index, value)
    }
    /**
     * `repeated .unhinged.document_store.Document documents = 1;`
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("clearDocuments")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.Document, DocumentsProxy>.clear() {
      _builder.clearDocuments()
    }

  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.PutDocumentsRequest.copy(block: `unhinged.document_store`.PutDocumentsRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.PutDocumentsRequest =
  `unhinged.document_store`.PutDocumentsRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

