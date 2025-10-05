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

@kotlin.jvm.JvmName("-initializehealthCheckResponse")
public inline fun healthCheckResponse(block: unhinged.document_store.HealthCheckResponseKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.HealthCheckResponse =
  unhinged.document_store.HealthCheckResponseKt.Dsl._create(unhinged.document_store.DocumentStore.HealthCheckResponse.newBuilder()).apply { block() }._build()
/**
 * Protobuf type `unhinged.document_store.HealthCheckResponse`
 */
public object HealthCheckResponseKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.HealthCheckResponse.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.HealthCheckResponse.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.HealthCheckResponse = _builder.build()

    /**
     * `bool healthy = 1;`
     */
    public var healthy: kotlin.Boolean
      @JvmName("getHealthy")
      get() = _builder.getHealthy()
      @JvmName("setHealthy")
      set(value) {
        _builder.setHealthy(value)
      }
    /**
     * `bool healthy = 1;`
     */
    public fun clearHealthy() {
      _builder.clearHealthy()
    }

    /**
     * `string status = 2;`
     */
    public var status: kotlin.String
      @JvmName("getStatus")
      get() = _builder.getStatus()
      @JvmName("setStatus")
      set(value) {
        _builder.setStatus(value)
      }
    /**
     * `string status = 2;`
     */
    public fun clearStatus() {
      _builder.clearStatus()
    }

    /**
     * `.google.protobuf.Timestamp timestamp = 3;`
     */
    public var timestamp: com.google.protobuf.Timestamp
      @JvmName("getTimestamp")
      get() = _builder.getTimestamp()
      @JvmName("setTimestamp")
      set(value) {
        _builder.setTimestamp(value)
      }
    /**
     * `.google.protobuf.Timestamp timestamp = 3;`
     */
    public fun clearTimestamp() {
      _builder.clearTimestamp()
    }
    /**
     * `.google.protobuf.Timestamp timestamp = 3;`
     * @return Whether the timestamp field is set.
     */
    public fun hasTimestamp(): kotlin.Boolean {
      return _builder.hasTimestamp()
    }
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.HealthCheckResponse.copy(block: `unhinged.document_store`.HealthCheckResponseKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.HealthCheckResponse =
  `unhinged.document_store`.HealthCheckResponseKt.Dsl._create(this.toBuilder()).apply { block() }._build()

public val unhinged.document_store.DocumentStore.HealthCheckResponseOrBuilder.timestampOrNull: com.google.protobuf.Timestamp?
  get() = if (hasTimestamp()) getTimestamp() else null

