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

@kotlin.jvm.JvmName("-initializehealthCheckRequest")
public inline fun healthCheckRequest(block: unhinged.document_store.HealthCheckRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.HealthCheckRequest =
  unhinged.document_store.HealthCheckRequestKt.Dsl._create(unhinged.document_store.DocumentStore.HealthCheckRequest.newBuilder()).apply { block() }._build()
/**
 * ```
 * Health check
 * ```
 *
 * Protobuf type `unhinged.document_store.HealthCheckRequest`
 */
public object HealthCheckRequestKt {
  @kotlin.OptIn(com.google.protobuf.kotlin.OnlyForUseByGeneratedProtoCode::class)
  @com.google.protobuf.kotlin.ProtoDslMarker
  public class Dsl private constructor(
    private val _builder: unhinged.document_store.DocumentStore.HealthCheckRequest.Builder
  ) {
    public companion object {
      @kotlin.jvm.JvmSynthetic
      @kotlin.PublishedApi
      internal fun _create(builder: unhinged.document_store.DocumentStore.HealthCheckRequest.Builder): Dsl = Dsl(builder)
    }

    @kotlin.jvm.JvmSynthetic
    @kotlin.PublishedApi
    internal fun _build(): unhinged.document_store.DocumentStore.HealthCheckRequest = _builder.build()
  }
}
@kotlin.jvm.JvmSynthetic
public inline fun unhinged.document_store.DocumentStore.HealthCheckRequest.copy(block: `unhinged.document_store`.HealthCheckRequestKt.Dsl.() -> kotlin.Unit): unhinged.document_store.DocumentStore.HealthCheckRequest =
  `unhinged.document_store`.HealthCheckRequestKt.Dsl._create(this.toBuilder()).apply { block() }._build()

