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

@kotlin.jvm.JvmName("-initializedocument")
public inline fun document(block: unhinged.document_store.DocumentKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.Document =
  unhinged.document_store.DocumentKt.Dsl._create(unhinged.document_store.DocumentStore.Document.newBuilder()).apply { block() }._build()
/**
 * ```
 * Core document message
 * ```
 *
 * Protobuf type `unhinged.document_store.Document`
 */
public object DocumentKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.Document.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.Document.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.Document = _builder.build()

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
     * `string type = 2;`
     */
    public var type: kotlin.String
      @JvmName("getType")
      get() = _builder.getType()
      @JvmName("setType")
      set(value) {
        _builder.setType(value)
      }
    /**
     * `string type = 2;`
     */
    public fun clearType() {
      _builder.clearType()
    }

    /**
     * `string name = 3;`
     */
    public var name: kotlin.String
      @JvmName("getName")
      get() = _builder.getName()
      @JvmName("setName")
      set(value) {
        _builder.setName(value)
      }
    /**
     * `string name = 3;`
     */
    public fun clearName() {
      _builder.clearName()
    }

    /**
     * `string namespace = 4;`
     */
    public var namespace: kotlin.String
      @JvmName("getNamespace")
      get() = _builder.getNamespace()
      @JvmName("setNamespace")
      set(value) {
        _builder.setNamespace(value)
      }
    /**
     * `string namespace = 4;`
     */
    public fun clearNamespace() {
      _builder.clearNamespace()
    }

    /**
     * `int32 version = 5;`
     */
    public var version: kotlin.Int
      @JvmName("getVersion")
      get() = _builder.getVersion()
      @JvmName("setVersion")
      set(value) {
        _builder.setVersion(value)
      }
    /**
     * `int32 version = 5;`
     */
    public fun clearVersion() {
      _builder.clearVersion()
    }

    /**
     * `string body_json = 6;`
     */
    public var bodyJson: kotlin.String
      @JvmName("getBodyJson")
      get() = _builder.getBodyJson()
      @JvmName("setBodyJson")
      set(value) {
        _builder.setBodyJson(value)
      }
    /**
     * `string body_json = 6;`
     */
    public fun clearBodyJson() {
      _builder.clearBodyJson()
    }

    /**
     * `.google.protobuf.Struct metadata = 7;`
     */
    public var metadata: com.google.protobuf.Struct
      @JvmName("getMetadata")
      get() = _builder.getMetadata()
      @JvmName("setMetadata")
      set(value) {
        _builder.setMetadata(value)
      }
    /**
     * `.google.protobuf.Struct metadata = 7;`
     */
    public fun clearMetadata() {
      _builder.clearMetadata()
    }
    /**
     * `.google.protobuf.Struct metadata = 7;`
     * @return Whether the metadata field is set.
     */
    public fun hasMetadata(): kotlin.Boolean {
      return _builder.hasMetadata()
    }

    /**
     * An uninstantiable, behaviorless type to represent the field in
     * generics.
     */
    @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
    public class TagsProxy private constructor() : com.google.protobuf.kotlin.DslProxy()
    /**
     * `repeated string tags = 8;`
     * @return A list containing the tags.
     */
    public val tags: com.google.protobuf.kotlin.DslList<kotlin.String, TagsProxy>
      @kotlin.jvm.JvmSynthetic
      get() = com.google.protobuf.kotlin.DslList(
        _builder.getTagsList()
      )
    /**
     * `repeated string tags = 8;`
     * @param value The tags to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addTags")
    public fun com.google.protobuf.kotlin.DslList<kotlin.String, TagsProxy>.add(value: kotlin.String) {
      _builder.addTags(value)
    }
    /**
     * `repeated string tags = 8;`
     * @param value The tags to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignTags")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<kotlin.String, TagsProxy>.plusAssign(value: kotlin.String) {
      add(value)
    }
    /**
     * `repeated string tags = 8;`
     * @param values The tags to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addAllTags")
    public fun com.google.protobuf.kotlin.DslList<kotlin.String, TagsProxy>.addAll(values: kotlin.collections.Iterable<kotlin.String>) {
      _builder.addAllTags(values)
    }
    /**
     * `repeated string tags = 8;`
     * @param values The tags to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignAllTags")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<kotlin.String, TagsProxy>.plusAssign(values: kotlin.collections.Iterable<kotlin.String>) {
      addAll(values)
    }
    /**
     * `repeated string tags = 8;`
     * @param index The index to set the value at.
     * @param value The tags to set.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("setTags")
    public operator fun com.google.protobuf.kotlin.DslList<kotlin.String, TagsProxy>.set(index: kotlin.Int, value: kotlin.String) {
      _builder.setTags(index, value)
    }/**
     * `repeated string tags = 8;`
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("clearTags")
    public fun com.google.protobuf.kotlin.DslList<kotlin.String, TagsProxy>.clear() {
      _builder.clearTags()
    }
    /**
     * `.google.protobuf.Timestamp created_at = 9;`
     */
    public var createdAt: com.google.protobuf.Timestamp
      @JvmName("getCreatedAt")
      get() = _builder.getCreatedAt()
      @JvmName("setCreatedAt")
      set(value) {
        _builder.setCreatedAt(value)
      }
    /**
     * `.google.protobuf.Timestamp created_at = 9;`
     */
    public fun clearCreatedAt() {
      _builder.clearCreatedAt()
    }
    /**
     * `.google.protobuf.Timestamp created_at = 9;`
     * @return Whether the createdAt field is set.
     */
    public fun hasCreatedAt(): kotlin.Boolean {
      return _builder.hasCreatedAt()
    }

    /**
     * `string created_by = 10;`
     */
    public var createdBy: kotlin.String
      @JvmName("getCreatedBy")
      get() = _builder.getCreatedBy()
      @JvmName("setCreatedBy")
      set(value) {
        _builder.setCreatedBy(value)
      }
    /**
     * `string created_by = 10;`
     */
    public fun clearCreatedBy() {
      _builder.clearCreatedBy()
    }

    /**
     * `string created_by_type = 11;`
     */
    public var createdByType: kotlin.String
      @JvmName("getCreatedByType")
      get() = _builder.getCreatedByType()
      @JvmName("setCreatedByType")
      set(value) {
        _builder.setCreatedByType(value)
      }
    /**
     * `string created_by_type = 11;`
     */
    public fun clearCreatedByType() {
      _builder.clearCreatedByType()
    }

    /**
     * `string session_id = 12;`
     */
    public var sessionId: kotlin.String
      @JvmName("getSessionId")
      get() = _builder.getSessionId()
      @JvmName("setSessionId")
      set(value) {
        _builder.setSessionId(value)
      }
    /**
     * `string session_id = 12;`
     */
    public fun clearSessionId() {
      _builder.clearSessionId()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.Document.copy(block: `unhinged.document_store`.DocumentKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.Document =
  `unhinged.document_store`.DocumentKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.DocumentOrBuilder.metadataOrNull: com.google.protobuf.Struct?
  get() = if (hasMetadata()) getMetadata() else null

public val unhinged.document_store.DocumentStore.DocumentOrBuilder.createdAtOrNull: com.google.protobuf.Timestamp?
  get() = if (hasCreatedAt()) getCreatedAt() else null

