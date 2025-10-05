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

@kotlin.jvm.JvmName("-initializegetDocumentRequest")
public inline fun getDocumentRequest(block: unhinged.document_store.GetDocumentRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.GetDocumentRequest =
  unhinged.document_store.GetDocumentRequestKt.Dsl._create(unhinged.document_store.DocumentStore.GetDocumentRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * Get single document
 * ```
 *
 * Protobuf type `unhinged.document_store.GetDocumentRequest`
 */
public object GetDocumentRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.GetDocumentRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.GetDocumentRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.GetDocumentRequest = _builder.build()

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
     * `optional int32 version = 2;`
     */
    public fun clearVersion() {
      _builder.clearVersion()
    }
    /**
     * `optional int32 version = 2;`
     * @return Whether the version field is set.
     */
    public fun hasVersion(): kotlin.Boolean {
      return _builder.hasVersion()
    }

    /**
     * `optional string tag = 3;`
     */
    public var tag: kotlin.String
      @JvmName("getTag")
      get() = _builder.getTag()
      @JvmName("setTag")
      set(value) {
        _builder.setTag(value)
      }
    /**
     * `optional string tag = 3;`
     */
    public fun clearTag() {
      _builder.clearTag()
    }
    /**
     * `optional string tag = 3;`
     * @return Whether the tag field is set.
     */
    public fun hasTag(): kotlin.Boolean {
      return _builder.hasTag()
    }

    /**
     * `bool include_body = 4;`
     */
    public var includeBody: kotlin.Boolean
      @JvmName("getIncludeBody")
      get() = _builder.getIncludeBody()
      @JvmName("setIncludeBody")
      set(value) {
        _builder.setIncludeBody(value)
      }
    /**
     * `bool include_body = 4;`
     */
    public fun clearIncludeBody() {
      _builder.clearIncludeBody()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.GetDocumentRequest.copy(block: `unhinged.document_store`.GetDocumentRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.GetDocumentRequest =
  `unhinged.document_store`.GetDocumentRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

