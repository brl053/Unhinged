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

@kotlin.jvm.JvmName("-initializelistDocumentVersionsRequest")
public inline fun listDocumentVersionsRequest(block: unhinged.document_store.ListDocumentVersionsRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ListDocumentVersionsRequest =
  unhinged.document_store.ListDocumentVersionsRequestKt.Dsl._create(unhinged.document_store.DocumentStore.ListDocumentVersionsRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * List document versions
 * ```
 *
 * Protobuf type `unhinged.document_store.ListDocumentVersionsRequest`
 */
public object ListDocumentVersionsRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.ListDocumentVersionsRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.ListDocumentVersionsRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.ListDocumentVersionsRequest = _builder.build()

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
     * `optional .google.protobuf.Timestamp pagination_token = 2;`
     */
    public var paginationToken: com.google.protobuf.Timestamp
      @JvmName("getPaginationToken")
      get() = _builder.getPaginationToken()
      @JvmName("setPaginationToken")
      set(value) {
        _builder.setPaginationToken(value)
      }
    /**
     * `optional .google.protobuf.Timestamp pagination_token = 2;`
     */
    public fun clearPaginationToken() {
      _builder.clearPaginationToken()
    }
    /**
     * `optional .google.protobuf.Timestamp pagination_token = 2;`
     * @return Whether the paginationToken field is set.
     */
    public fun hasPaginationToken(): kotlin.Boolean {
      return _builder.hasPaginationToken()
    }
    public val ListDocumentVersionsRequestKt.Dsl.paginationTokenOrNull: com.google.protobuf.Timestamp?
      get() = _builder.paginationTokenOrNull

    /**
     * `int32 page_size = 3;`
     */
    public var pageSize: kotlin.Int
      @JvmName("getPageSize")
      get() = _builder.getPageSize()
      @JvmName("setPageSize")
      set(value) {
        _builder.setPageSize(value)
      }
    /**
     * `int32 page_size = 3;`
     */
    public fun clearPageSize() {
      _builder.clearPageSize()
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
public inline fun unhinged.document_store.DocumentStore.ListDocumentVersionsRequest.copy(block: `unhinged.document_store`.ListDocumentVersionsRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ListDocumentVersionsRequest =
  `unhinged.document_store`.ListDocumentVersionsRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.ListDocumentVersionsRequestOrBuilder.paginationTokenOrNull: com.google.protobuf.Timestamp?
  get() = if (hasPaginationToken()) getPaginationToken() else null

