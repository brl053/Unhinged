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

@kotlin.jvm.JvmName("-initializetagEvent")
public inline fun tagEvent(block: unhinged.document_store.TagEventKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.TagEvent =
  unhinged.document_store.TagEventKt.Dsl._create(unhinged.document_store.DocumentStore.TagEvent.newBuilder()).apply { block() }._build()
/**
 * ```
 * Tag event for audit trail
 * ```
 *
 * Protobuf type `unhinged.document_store.TagEvent`
 */
public object TagEventKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.TagEvent.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.TagEvent.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.TagEvent = _builder.build()

    /**
     * `string tag_event_uuid = 1;`
     */
    public var tagEventUuid: kotlin.String
      @JvmName("getTagEventUuid")
      get() = _builder.getTagEventUuid()
      @JvmName("setTagEventUuid")
      set(value) {
        _builder.setTagEventUuid(value)
      }
    /**
     * `string tag_event_uuid = 1;`
     */
    public fun clearTagEventUuid() {
      _builder.clearTagEventUuid()
    }

    /**
     * `string document_uuid = 2;`
     */
    public var documentUuid: kotlin.String
      @JvmName("getDocumentUuid")
      get() = _builder.getDocumentUuid()
      @JvmName("setDocumentUuid")
      set(value) {
        _builder.setDocumentUuid(value)
      }
    /**
     * `string document_uuid = 2;`
     */
    public fun clearDocumentUuid() {
      _builder.clearDocumentUuid()
    }

    /**
     * `int32 document_version = 3;`
     */
    public var documentVersion: kotlin.Int
      @JvmName("getDocumentVersion")
      get() = _builder.getDocumentVersion()
      @JvmName("setDocumentVersion")
      set(value) {
        _builder.setDocumentVersion(value)
      }
    /**
     * `int32 document_version = 3;`
     */
    public fun clearDocumentVersion() {
      _builder.clearDocumentVersion()
    }

    /**
     * `string tag = 4;`
     */
    public var tag: kotlin.String
      @JvmName("getTag")
      get() = _builder.getTag()
      @JvmName("setTag")
      set(value) {
        _builder.setTag(value)
      }
    /**
     * `string tag = 4;`
     */
    public fun clearTag() {
      _builder.clearTag()
    }

    /**
     * `string operation = 5;`
     */
    public var operation: kotlin.String
      @JvmName("getOperation")
      get() = _builder.getOperation()
      @JvmName("setOperation")
      set(value) {
        _builder.setOperation(value)
      }
    /**
     * `string operation = 5;`
     */
    public fun clearOperation() {
      _builder.clearOperation()
    }

    /**
     * `.google.protobuf.Timestamp created_at = 6;`
     */
    public var createdAt: com.google.protobuf.Timestamp
      @JvmName("getCreatedAt")
      get() = _builder.getCreatedAt()
      @JvmName("setCreatedAt")
      set(value) {
        _builder.setCreatedAt(value)
      }
    /**
     * `.google.protobuf.Timestamp created_at = 6;`
     */
    public fun clearCreatedAt() {
      _builder.clearCreatedAt()
    }
    /**
     * `.google.protobuf.Timestamp created_at = 6;`
     * @return Whether the createdAt field is set.
     */
    public fun hasCreatedAt(): kotlin.Boolean {
      return _builder.hasCreatedAt()
    }

    /**
     * `string created_by = 7;`
     */
    public var createdBy: kotlin.String
      @JvmName("getCreatedBy")
      get() = _builder.getCreatedBy()
      @JvmName("setCreatedBy")
      set(value) {
        _builder.setCreatedBy(value)
      }
    /**
     * `string created_by = 7;`
     */
    public fun clearCreatedBy() {
      _builder.clearCreatedBy()
    }

    /**
     * `string created_by_type = 8;`
     */
    public var createdByType: kotlin.String
      @JvmName("getCreatedByType")
      get() = _builder.getCreatedByType()
      @JvmName("setCreatedByType")
      set(value) {
        _builder.setCreatedByType(value)
      }
    /**
     * `string created_by_type = 8;`
     */
    public fun clearCreatedByType() {
      _builder.clearCreatedByType()
    }

    /**
     * `string session_id = 9;`
     */
    public var sessionId: kotlin.String
      @JvmName("getSessionId")
      get() = _builder.getSessionId()
      @JvmName("setSessionId")
      set(value) {
        _builder.setSessionId(value)
      }
    /**
     * `string session_id = 9;`
     */
    public fun clearSessionId() {
      _builder.clearSessionId()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.TagEvent.copy(block: `unhinged.document_store`.TagEventKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.TagEvent =
  `unhinged.document_store`.TagEventKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.TagEventOrBuilder.createdAtOrNull: com.google.protobuf.Timestamp?
  get() = if (hasCreatedAt()) getCreatedAt() else null

