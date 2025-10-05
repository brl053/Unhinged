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

@kotlin.jvm.JvmName("-initializeactiveTag")
public inline fun activeTag(block: unhinged.document_store.ActiveTagKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ActiveTag =
  unhinged.document_store.ActiveTagKt.Dsl._create(unhinged.document_store.DocumentStore.ActiveTag.newBuilder()).apply { block() }._build()
/**
 * ```
 * Active tag information
 * ```
 *
 * Protobuf type `unhinged.document_store.ActiveTag`
 */
public object ActiveTagKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.ActiveTag.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.ActiveTag.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.ActiveTag = _builder.build()

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
     * `int32 document_version = 2;`
     */
    public var documentVersion: kotlin.Int
      @JvmName("getDocumentVersion")
      get() = _builder.getDocumentVersion()
      @JvmName("setDocumentVersion")
      set(value) {
        _builder.setDocumentVersion(value)
      }
    /**
     * `int32 document_version = 2;`
     */
    public fun clearDocumentVersion() {
      _builder.clearDocumentVersion()
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
     * `.google.protobuf.Timestamp updated_at = 4;`
     */
    public var updatedAt: com.google.protobuf.Timestamp
      @JvmName("getUpdatedAt")
      get() = _builder.getUpdatedAt()
      @JvmName("setUpdatedAt")
      set(value) {
        _builder.setUpdatedAt(value)
      }
    /**
     * `.google.protobuf.Timestamp updated_at = 4;`
     */
    public fun clearUpdatedAt() {
      _builder.clearUpdatedAt()
    }
    /**
     * `.google.protobuf.Timestamp updated_at = 4;`
     * @return Whether the updatedAt field is set.
     */
    public fun hasUpdatedAt(): kotlin.Boolean {
      return _builder.hasUpdatedAt()
    }

    /**
     * `string updated_by = 5;`
     */
    public var updatedBy: kotlin.String
      @JvmName("getUpdatedBy")
      get() = _builder.getUpdatedBy()
      @JvmName("setUpdatedBy")
      set(value) {
        _builder.setUpdatedBy(value)
      }
    /**
     * `string updated_by = 5;`
     */
    public fun clearUpdatedBy() {
      _builder.clearUpdatedBy()
    }

    /**
     * `string updated_by_type = 6;`
     */
    public var updatedByType: kotlin.String
      @JvmName("getUpdatedByType")
      get() = _builder.getUpdatedByType()
      @JvmName("setUpdatedByType")
      set(value) {
        _builder.setUpdatedByType(value)
      }
    /**
     * `string updated_by_type = 6;`
     */
    public fun clearUpdatedByType() {
      _builder.clearUpdatedByType()
    }

    /**
     * `string session_id = 7;`
     */
    public var sessionId: kotlin.String
      @JvmName("getSessionId")
      get() = _builder.getSessionId()
      @JvmName("setSessionId")
      set(value) {
        _builder.setSessionId(value)
      }
    /**
     * `string session_id = 7;`
     */
    public fun clearSessionId() {
      _builder.clearSessionId()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.ActiveTag.copy(block: `unhinged.document_store`.ActiveTagKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.ActiveTag =
  `unhinged.document_store`.ActiveTagKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.ActiveTagOrBuilder.updatedAtOrNull: com.google.protobuf.Timestamp?
  get() = if (hasUpdatedAt()) getUpdatedAt() else null

