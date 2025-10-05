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

@kotlin.jvm.JvmName("-initializelistDocumentsRequest")
public inline fun listDocumentsRequest(block: unhinged.document_store.ListDocumentsRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ListDocumentsRequest =
  unhinged.document_store.ListDocumentsRequestKt.Dsl._create(unhinged.document_store.DocumentStore.ListDocumentsRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * List documents with filtering
 * ```
 *
 * Protobuf type `unhinged.document_store.ListDocumentsRequest`
 */
public object ListDocumentsRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.ListDocumentsRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.ListDocumentsRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.ListDocumentsRequest = _builder.build()

    /**
     * `optional string namespace = 1;`
     */
    public var namespace: kotlin.String
      @JvmName("getNamespace")
      get() = _builder.getNamespace()
      @JvmName("setNamespace")
      set(value) {
        _builder.setNamespace(value)
      }
    /**
     * `optional string namespace = 1;`
     */
    public fun clearNamespace() {
      _builder.clearNamespace()
    }
    /**
     * `optional string namespace = 1;`
     * @return Whether the namespace field is set.
     */
    public fun hasNamespace(): kotlin.Boolean {
      return _builder.hasNamespace()
    }

    /**
     * `optional string type = 2;`
     */
    public var type: kotlin.String
      @JvmName("getType")
      get() = _builder.getType()
      @JvmName("setType")
      set(value) {
        _builder.setType(value)
      }
    /**
     * `optional string type = 2;`
     */
    public fun clearType() {
      _builder.clearType()
    }
    /**
     * `optional string type = 2;`
     * @return Whether the type field is set.
     */
    public fun hasType(): kotlin.Boolean {
      return _builder.hasType()
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
     * `optional string session_id = 4;`
     */
    public var sessionId: kotlin.String
      @JvmName("getSessionId")
      get() = _builder.getSessionId()
      @JvmName("setSessionId")
      set(value) {
        _builder.setSessionId(value)
      }
    /**
     * `optional string session_id = 4;`
     */
    public fun clearSessionId() {
      _builder.clearSessionId()
    }
    /**
     * `optional string session_id = 4;`
     * @return Whether the sessionId field is set.
     */
    public fun hasSessionId(): kotlin.Boolean {
      return _builder.hasSessionId()
    }

    /**
     * `optional .google.protobuf.Timestamp pagination_token = 5;`
     */
    public var paginationToken: com.google.protobuf.Timestamp
      @JvmName("getPaginationToken")
      get() = _builder.getPaginationToken()
      @JvmName("setPaginationToken")
      set(value) {
        _builder.setPaginationToken(value)
      }
    /**
     * `optional .google.protobuf.Timestamp pagination_token = 5;`
     */
    public fun clearPaginationToken() {
      _builder.clearPaginationToken()
    }
    /**
     * `optional .google.protobuf.Timestamp pagination_token = 5;`
     * @return Whether the paginationToken field is set.
     */
    public fun hasPaginationToken(): kotlin.Boolean {
      return _builder.hasPaginationToken()
    }
    public val ListDocumentsRequestKt.Dsl.paginationTokenOrNull: com.google.protobuf.Timestamp?
      get() = _builder.paginationTokenOrNull

    /**
     * `int32 page_size = 6;`
     */
    public var pageSize: kotlin.Int
      @JvmName("getPageSize")
      get() = _builder.getPageSize()
      @JvmName("setPageSize")
      set(value) {
        _builder.setPageSize(value)
      }
    /**
     * `int32 page_size = 6;`
     */
    public fun clearPageSize() {
      _builder.clearPageSize()
    }

    /**
     * `bool include_body = 7;`
     */
    public var includeBody: kotlin.Boolean
      @JvmName("getIncludeBody")
      get() = _builder.getIncludeBody()
      @JvmName("setIncludeBody")
      set(value) {
        _builder.setIncludeBody(value)
      }
    /**
     * `bool include_body = 7;`
     */
    public fun clearIncludeBody() {
      _builder.clearIncludeBody()
    }

    /**
     * `bool latest_versions_only = 8;`
     */
    public var latestVersionsOnly: kotlin.Boolean
      @JvmName("getLatestVersionsOnly")
      get() = _builder.getLatestVersionsOnly()
      @JvmName("setLatestVersionsOnly")
      set(value) {
        _builder.setLatestVersionsOnly(value)
      }
    /**
     * `bool latest_versions_only = 8;`
     */
    public fun clearLatestVersionsOnly() {
      _builder.clearLatestVersionsOnly()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.ListDocumentsRequest.copy(block: `unhinged.document_store`.ListDocumentsRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ListDocumentsRequest =
  `unhinged.document_store`.ListDocumentsRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.ListDocumentsRequestOrBuilder.paginationTokenOrNull: com.google.protobuf.Timestamp?
  get() = if (hasPaginationToken()) getPaginationToken() else null

