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

@kotlin.jvm.JvmName("-initializeputDocumentRequest")
public inline fun putDocumentRequest(block: unhinged.document_store.PutDocumentRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.PutDocumentRequest =
  unhinged.document_store.PutDocumentRequestKt.Dsl._create(unhinged.document_store.DocumentStore.PutDocumentRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * Create/Update document request
 * ```
 *
 * Protobuf type `unhinged.document_store.PutDocumentRequest`
 */
public object PutDocumentRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.PutDocumentRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.PutDocumentRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.PutDocumentRequest = _builder.build()

    /**
     * `.unhinged.document_store.Document document = 1;`
     */
    public var document: unhinged.document_store.DocumentStore.Document
      @JvmName("getDocument")
      get() = _builder.getDocument()
      @JvmName("setDocument")
      set(value) {
        _builder.setDocument(value)
      }
    /**
     * `.unhinged.document_store.Document document = 1;`
     */
    public fun clearDocument() {
      _builder.clearDocument()
    }
    /**
     * `.unhinged.document_store.Document document = 1;`
     * @return Whether the document field is set.
     */
    public fun hasDocument(): kotlin.Boolean {
      return _builder.hasDocument()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.PutDocumentRequest.copy(block: `unhinged.document_store`.PutDocumentRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.PutDocumentRequest =
  `unhinged.document_store`.PutDocumentRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.PutDocumentRequestOrBuilder.documentOrNull: unhinged.document_store.DocumentStore.Document?
  get() = if (hasDocument()) getDocument() else null

