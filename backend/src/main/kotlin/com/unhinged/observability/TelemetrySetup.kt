// ============================================================================
// Unhinged Backend Telemetry Setup
// ============================================================================
//
// @file TelemetrySetup.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-07
// @description OpenTelemetry configuration for Unhinged backend
//
// LEGEND: Observability instrumentation for consciousness architecture
// KEY: Traces, metrics, and logs integration with LGTM stack
// MAP: Complete telemetry pipeline for distributed consciousness services
// ============================================================================

package com.unhinged.observability

import io.opentelemetry.api.OpenTelemetry
import io.opentelemetry.api.common.Attributes
import io.opentelemetry.api.trace.Tracer
import io.opentelemetry.api.metrics.Meter
import io.opentelemetry.exporter.otlp.trace.OtlpGrpcSpanExporter
import io.opentelemetry.exporter.otlp.metrics.OtlpGrpcMetricExporter
import io.opentelemetry.sdk.OpenTelemetrySdk
import io.opentelemetry.sdk.resources.Resource
import io.opentelemetry.sdk.trace.SdkTracerProvider
import io.opentelemetry.sdk.metrics.SdkMeterProvider
import io.opentelemetry.semconv.resource.attributes.ResourceAttributes
import org.slf4j.LoggerFactory

/**
 * OpenTelemetry setup for Unhinged backend
 * Integrates with existing infrastructure and logging
 */
object TelemetrySetup {
    private val logger = LoggerFactory.getLogger(TelemetrySetup::class.java)
    
    private val resource = Resource.getDefault()
        .merge(Resource.create(
            Attributes.of(
                ResourceAttributes.SERVICE_NAME, "unhinged-backend",
                ResourceAttributes.SERVICE_VERSION, "1.0.0",
                ResourceAttributes.SERVICE_NAMESPACE, "unhinged",
                ResourceAttributes.DEPLOYMENT_ENVIRONMENT, "development"
            )
        ))
    
    val openTelemetry: OpenTelemetry by lazy {
        logger.info("🔍 Initializing OpenTelemetry for Unhinged backend...")
        
        try {
            OpenTelemetrySdk.builder()
                .setTracerProvider(
                    SdkTracerProvider.builder()
                        .addSpanProcessor(
                            io.opentelemetry.sdk.trace.export.BatchSpanProcessor.builder(
                                OtlpGrpcSpanExporter.builder()
                                    .setEndpoint("http://otel-collector:4319") // Non-conflicting port
                                    .build()
                            ).build()
                        )
                        .setResource(resource)
                        .build()
                )
                .setMeterProvider(
                    SdkMeterProvider.builder()
                        .registerMetricReader(
                            io.opentelemetry.sdk.metrics.export.PeriodicMetricReader.builder(
                                OtlpGrpcMetricExporter.builder()
                                    .setEndpoint("http://otel-collector:4319")
                                    .build()
                            ).build()
                        )
                        .setResource(resource)
                        .build()
                )
                .build()
        } catch (e: Exception) {
            logger.warn("⚠️ Failed to initialize OpenTelemetry, using no-op implementation: ${e.message}")
            OpenTelemetry.noop()
        }
    }
    
    val tracer: Tracer = openTelemetry.getTracer("unhinged-backend")
    val meter: Meter = openTelemetry.getMeter("unhinged-backend")
    
    // Metrics for existing endpoints
    val httpRequestDuration = meter
        .histogramBuilder("http.server.duration")
        .setDescription("HTTP request duration")
        .setUnit("ms")
        .build()
    
    val chatRequestsTotal = meter
        .counterBuilder("unhinged.chat.requests.total")
        .setDescription("Total chat requests processed")
        .build()
    
    val serviceCallsTotal = meter
        .counterBuilder("unhinged.service.calls.total")
        .setDescription("Total calls to downstream services")
        .build()
    
    val activeConversations = meter
        .upDownCounterBuilder("unhinged.conversations.active")
        .setDescription("Number of active conversations")
        .build()
}
