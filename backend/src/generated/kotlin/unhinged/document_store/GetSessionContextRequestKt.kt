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

@kotlin.jvm.JvmName("-initializegetSessionContextRequest")
public inline fun getSessionContextRequest(block: unhinged.document_store.GetSessionContextRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.GetSessionContextRequest =
  unhinged.document_store.GetSessionContextRequestKt.Dsl._create(unhinged.document_store.DocumentStore.GetSessionContextRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * Session context queries
 * ```
 *
 * Protobuf type `unhinged.document_store.GetSessionContextRequest`
 */
public object GetSessionContextRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.GetSessionContextRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.GetSessionContextRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.GetSessionContextRequest = _builder.build()

    /**
     * `string session_id = 1;`
     */
    public var sessionId: kotlin.String
      @JvmName("getSessionId")
      get() = _builder.getSessionId()
      @JvmName("setSessionId")
      set(value) {
        _builder.setSessionId(value)
      }
    /**
     * `string session_id = 1;`
     */
    public fun clearSessionId() {
      _builder.clearSessionId()
    }

    /**
     * An uninstantiable, behaviorless type to represent the field in
     * generics.
     */
    @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
    public class DocumentTypesProxy private constructor() : com.google.protobuf.kotlin.DslProxy()
    /**
     * `repeated string document_types = 2;`
     * @return A list containing the documentTypes.
     */
    public val documentTypes: com.google.protobuf.kotlin.DslList<kotlin.String, DocumentTypesProxy>
      @kotlin.jvm.JvmSynthetic
      get() = com.google.protobuf.kotlin.DslList(
        _builder.getDocumentTypesList()
      )
    /**
     * `repeated string document_types = 2;`
     * @param value The documentTypes to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addDocumentTypes")
    public fun com.google.protobuf.kotlin.DslList<kotlin.String, DocumentTypesProxy>.add(value: kotlin.String) {
      _builder.addDocumentTypes(value)
    }
    /**
     * `repeated string document_types = 2;`
     * @param value The documentTypes to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignDocumentTypes")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<kotlin.String, DocumentTypesProxy>.plusAssign(value: kotlin.String) {
      add(value)
    }
    /**
     * `repeated string document_types = 2;`
     * @param values The documentTypes to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("addAllDocumentTypes")
    public fun com.google.protobuf.kotlin.DslList<kotlin.String, DocumentTypesProxy>.addAll(values: kotlin.collections.Iterable<kotlin.String>) {
      _builder.addAllDocumentTypes(values)
    }
    /**
     * `repeated string document_types = 2;`
     * @param values The documentTypes to add.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("plusAssignAllDocumentTypes")
    @Suppress("NOTHING_TO_INLINE")
    public inline operator fun com.google.protobuf.kotlin.DslList<kotlin.String, DocumentTypesProxy>.plusAssign(values: kotlin.collections.Iterable<kotlin.String>) {
      addAll(values)
    }
    /**
     * `repeated string document_types = 2;`
     * @param index The index to set the value at.
     * @param value The documentTypes to set.
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("setDocumentTypes")
    public operator fun com.google.protobuf.kotlin.DslList<kotlin.String, DocumentTypesProxy>.set(index: kotlin.Int, value: kotlin.String) {
      _builder.setDocumentTypes(index, value)
    }/**
     * `repeated string document_types = 2;`
     */
    @kotlin.jvm.JvmSynthetic
    @kotlin.jvm.JvmName("clearDocumentTypes")
    public fun com.google.protobuf.kotlin.DslList<kotlin.String, DocumentTypesProxy>.clear() {
      _builder.clearDocumentTypes()
    }
    /**
     * `optional .google.protobuf.Timestamp since = 3;`
     */
    public var since: com.google.protobuf.Timestamp
      @JvmName("getSince")
      get() = _builder.getSince()
      @JvmName("setSince")
      set(value) {
        _builder.setSince(value)
      }
    /**
     * `optional .google.protobuf.Timestamp since = 3;`
     */
    public fun clearSince() {
      _builder.clearSince()
    }
    /**
     * `optional .google.protobuf.Timestamp since = 3;`
     * @return Whether the since field is set.
     */
    public fun hasSince(): kotlin.Boolean {
      return _builder.hasSince()
    }
    public val GetSessionContextRequestKt.Dsl.sinceOrNull: com.google.protobuf.Timestamp?
      get() = _builder.sinceOrNull

    /**
     * `int32 limit = 4;`
     */
    public var limit: kotlin.Int
      @JvmName("getLimit")
      get() = _builder.getLimit()
      @JvmName("setLimit")
      set(value) {
        _builder.setLimit(value)
      }
    /**
     * `int32 limit = 4;`
     */
    public fun clearLimit() {
      _builder.clearLimit()
    }

    /**
     * `bool include_body = 5;`
     */
    public var includeBody: kotlin.Boolean
      @JvmName("getIncludeBody")
      get() = _builder.getIncludeBody()
      @JvmName("setIncludeBody")
      set(value) {
        _builder.setIncludeBody(value)
      }
    /**
     * `bool include_body = 5;`
     */
    public fun clearIncludeBody() {
      _builder.clearIncludeBody()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.GetSessionContextRequest.copy(block: `unhinged.document_store`.GetSessionContextRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.GetSessionContextRequest =
  `unhinged.document_store`.GetSessionContextRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.GetSessionContextRequestOrBuilder.sinceOrNull: com.google.protobuf.Timestamp?
  get() = if (hasSince()) getSince() else null

