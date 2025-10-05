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

@kotlin.jvm.JvmName("-initializelistActiveTagsRequest")
public inline fun listActiveTagsRequest(block: unhinged.document_store.ListActiveTagsRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ListActiveTagsRequest =
  unhinged.document_store.ListActiveTagsRequestKt.Dsl._create(unhinged.document_store.DocumentStore.ListActiveTagsRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * List active tags for a document
 * ```
 *
 * Protobuf type `unhinged.document_store.ListActiveTagsRequest`
 */
public object ListActiveTagsRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.ListActiveTagsRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.ListActiveTagsRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.ListActiveTagsRequest = _builder.build()

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
     * `optional int32 document_version = 2;`
     */
    public var documentVersion: kotlin.Int
      @JvmName("getDocumentVersion")
      get() = _builder.getDocumentVersion()
      @JvmName("setDocumentVersion")
      set(value) {
        _builder.setDocumentVersion(value)
      }
    /**
     * `optional int32 document_version = 2;`
     */
    public fun clearDocumentVersion() {
      _builder.clearDocumentVersion()
    }
    /**
     * `optional int32 document_version = 2;`
     * @return Whether the documentVersion field is set.
     */
    public fun hasDocumentVersion(): kotlin.Boolean {
      return _builder.hasDocumentVersion()
    }

    /**
     * `optional .google.protobuf.Timestamp pagination_token = 3;`
     */
    public var paginationToken: com.google.protobuf.Timestamp
      @JvmName("getPaginationToken")
      get() = _builder.getPaginationToken()
      @JvmName("setPaginationToken")
      set(value) {
        _builder.setPaginationToken(value)
      }
    /**
     * `optional .google.protobuf.Timestamp pagination_token = 3;`
     */
    public fun clearPaginationToken() {
      _builder.clearPaginationToken()
    }
    /**
     * `optional .google.protobuf.Timestamp pagination_token = 3;`
     * @return Whether the paginationToken field is set.
     */
    public fun hasPaginationToken(): kotlin.Boolean {
      return _builder.hasPaginationToken()
    }
    public val ListActiveTagsRequestKt.Dsl.paginationTokenOrNull: com.google.protobuf.Timestamp?
      get() = _builder.paginationTokenOrNull

    /**
     * `int32 page_size = 4;`
     */
    public var pageSize: kotlin.Int
      @JvmName("getPageSize")
      get() = _builder.getPageSize()
      @JvmName("setPageSize")
      set(value) {
        _builder.setPageSize(value)
      }
    /**
     * `int32 page_size = 4;`
     */
    public fun clearPageSize() {
      _builder.clearPageSize()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.ListActiveTagsRequest.copy(block: `unhinged.document_store`.ListActiveTagsRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ListActiveTagsRequest =
  `unhinged.document_store`.ListActiveTagsRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.ListActiveTagsRequestOrBuilder.paginationTokenOrNull: com.google.protobuf.Timestamp?
  get() = if (hasPaginationToken()) getPaginationToken() else null

