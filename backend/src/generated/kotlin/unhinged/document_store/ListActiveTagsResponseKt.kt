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

@kotlin.jvm.JvmName("-initializelistActiveTagsResponse")
public inline fun listActiveTagsResponse(block: unhinged.document_store.ListActiveTagsResponseKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ListActiveTagsResponse =
  unhinged.document_store.ListActiveTagsResponseKt.Dsl._create(unhinged.document_store.DocumentStore.ListActiveTagsResponse.newBuilder()).apply { block() }._build()
/**
 * Protobuf type `unhinged.document_store.ListActiveTagsResponse`
 */
public object ListActiveTagsResponseKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.ListActiveTagsResponse.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.ListActiveTagsResponse.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.ListActiveTagsResponse = _builder.build()

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
    public class TagsProxy private constructor() : com.google.protobuf.kotlin.DslProxy()
    /**
     * `repeated .unhinged.document_store.ActiveTag tags = 3;`
     */
     public val tags: com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.ActiveTag, TagsProxy>
      @kotlin.jvm.JvmSynthetic
      get() = com.google.protobuf.kotlin.DslList(
        _builder.getTagsList()
      )
    /**
     * `repeated .unhinged.document_store.ActiveTag tags = 3;`
     * @param value The tags to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addTags")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.ActiveTag, TagsProxy>.add(value: unhinged.document_store.DocumentStore.ActiveTag) {
      _builder.addTags(value)
    }
    /**
     * `repeated .unhinged.document_store.ActiveTag tags = 3;`
     * @param value The tags to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignTags")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.ActiveTag, TagsProxy>.plusAssign(value: unhinged.document_store.DocumentStore.ActiveTag) {
      add(value)
    }
    /**
     * `repeated .unhinged.document_store.ActiveTag tags = 3;`
     * @param values The tags to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addAllTags")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.ActiveTag, TagsProxy>.addAll(values: kotlin.collections.Iterable<unhinged.document_store.DocumentStore.ActiveTag>) {
      _builder.addAllTags(values)
    }
    /**
     * `repeated .unhinged.document_store.ActiveTag tags = 3;`
     * @param values The tags to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignAllTags")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.ActiveTag, TagsProxy>.plusAssign(values: kotlin.collections.Iterable<unhinged.document_store.DocumentStore.ActiveTag>) {
      addAll(values)
    }
    /**
     * `repeated .unhinged.document_store.ActiveTag tags = 3;`
     * @param index The index to set the value at.
     * @param value The tags to set.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("setTags")
    public operator fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.ActiveTag, TagsProxy>.set(index: kotlin.Int, value: unhinged.document_store.DocumentStore.ActiveTag) {
      _builder.setTags(index, value)
    }
    /**
     * `repeated .unhinged.document_store.ActiveTag tags = 3;`
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("clearTags")
    public fun com.google.protobuf.kotlin.DslList<unhinged.document_store.DocumentStore.ActiveTag, TagsProxy>.clear() {
      _builder.clearTags()
    }


    /**
     * `.google.protobuf.Timestamp next_pagination_token = 4;`
     */
    public var nextPaginationToken: com.google.protobuf.Timestamp
      @JvmName("getNextPaginationToken")
      get() = _builder.getNextPaginationToken()
      @JvmName("setNextPaginationToken")
      set(value) {
        _builder.setNextPaginationToken(value)
      }
    /**
     * `.google.protobuf.Timestamp next_pagination_token = 4;`
     */
    public fun clearNextPaginationToken() {
      _builder.clearNextPaginationToken()
    }
    /**
     * `.google.protobuf.Timestamp next_pagination_token = 4;`
     * @return Whether the nextPaginationToken field is set.
     */
    public fun hasNextPaginationToken(): kotlin.Boolean {
      return _builder.hasNextPaginationToken()
    }

    /**
     * `int32 total_count = 5;`
     */
    public var totalCount: kotlin.Int
      @JvmName("getTotalCount")
      get() = _builder.getTotalCount()
      @JvmName("setTotalCount")
      set(value) {
        _builder.setTotalCount(value)
      }
    /**
     * `int32 total_count = 5;`
     */
    public fun clearTotalCount() {
      _builder.clearTotalCount()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.ListActiveTagsResponse.copy(block: `unhinged.document_store`.ListActiveTagsResponseKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ListActiveTagsResponse =
  `unhinged.document_store`.ListActiveTagsResponseKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.ListActiveTagsResponseOrBuilder.nextPaginationTokenOrNull: com.google.protobuf.Timestamp?
  get() = if (hasNextPaginationToken()) getNextPaginationToken() else null

