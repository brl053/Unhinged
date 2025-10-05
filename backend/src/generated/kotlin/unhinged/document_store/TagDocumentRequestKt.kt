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

@kotlin.jvm.JvmName("-initializetagDocumentRequest")
public inline fun tagDocumentRequest(block: unhinged.document_store.TagDocumentRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.TagDocumentRequest =
  unhinged.document_store.TagDocumentRequestKt.Dsl._create(unhinged.document_store.DocumentStore.TagDocumentRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * Tag operations
 * ```
 *
 * Protobuf type `unhinged.document_store.TagDocumentRequest`
 */
public object TagDocumentRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.TagDocumentRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.TagDocumentRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.TagDocumentRequest = _builder.build()

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
     * `string tag = 3;`
     */
    public var tag: kotlin.String
      @JvmName("getTag")
      get() = _builder.getTag()
      @JvmName("setTag")
      set(value) {
        _builder.setTag(value)
      }
    /**
     * `string tag = 3;`
     */
    public fun clearTag() {
      _builder.clearTag()
    }

    /**
     * `string tagged_by = 4;`
     */
    public var taggedBy: kotlin.String
      @JvmName("getTaggedBy")
      get() = _builder.getTaggedBy()
      @JvmName("setTaggedBy")
      set(value) {
        _builder.setTaggedBy(value)
      }
    /**
     * `string tagged_by = 4;`
     */
    public fun clearTaggedBy() {
      _builder.clearTaggedBy()
    }

    /**
     * `string tagged_by_type = 5;`
     */
    public var taggedByType: kotlin.String
      @JvmName("getTaggedByType")
      get() = _builder.getTaggedByType()
      @JvmName("setTaggedByType")
      set(value) {
        _builder.setTaggedByType(value)
      }
    /**
     * `string tagged_by_type = 5;`
     */
    public fun clearTaggedByType() {
      _builder.clearTaggedByType()
    }

    /**
     * `string session_id = 6;`
     */
    public var sessionId: kotlin.String
      @JvmName("getSessionId")
      get() = _builder.getSessionId()
      @JvmName("setSessionId")
      set(value) {
        _builder.setSessionId(value)
      }
    /**
     * `string session_id = 6;`
     */
    public fun clearSessionId() {
      _builder.clearSessionId()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.TagDocumentRequest.copy(block: `unhinged.document_store`.TagDocumentRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.TagDocumentRequest =
  `unhinged.document_store`.TagDocumentRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

