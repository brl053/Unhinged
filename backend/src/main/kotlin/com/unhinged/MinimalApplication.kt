// ============================================================================
// Minimal Unhinged Backend - Production Ready Build Pipeline
// ============================================================================
//
// @file MinimalApplication.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-06
// @description Minimal working backend to establish production-ready build pipeline
//
// This is a simplified version to get the build working, then we can add features back
//
// ============================================================================

package com.unhinged

import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.server.response.*
import io.ktor.server.routing.*
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import org.slf4j.LoggerFactory

private val logger = LoggerFactory.getLogger("MinimalApplication")

@Serializable
data class HealthResponse(
    val status: String,
    val timestamp: Long,
    val version: String = "1.0.0",
    val services: Map<String, String> = mapOf(
        "backend" to "healthy",
        "protobuf" to "generated",
        "build" to "successful"
    )
)

@Serializable
data class ApiResponse(
    val message: String,
    val timestamp: Long,
    val version: String = "1.0.0"
)

@Serializable
data class StatusResponse(
    val api: String,
    val build: String,
    val protobuf: String,
    val timestamp: Long
)

@Serializable
data class ServiceHealthResponse(
    val service: String,
    val status: String,
    val timestamp: Long,
    val architecture: String? = null
)

fun main() {
    logger.info("🚀 Starting Minimal Unhinged Backend Server...")
    logger.info("📋 Establishing production-ready build pipeline...")
    
    embeddedServer(Netty, port = 8081, host = "0.0.0.0") {
        configureSerialization()
        configureCORS()
        configureRouting()
        
        logger.info("✅ Server configured and ready")
    }.start(wait = true)
}

fun Application.configureSerialization() {
    install(ContentNegotiation) {
        json(Json {
            prettyPrint = true
            isLenient = true
            ignoreUnknownKeys = true
        })
    }
}

fun Application.configureCORS() {
    install(CORS) {
        allowMethod(HttpMethod.Options)
        allowMethod(HttpMethod.Get)
        allowMethod(HttpMethod.Post)
        allowMethod(HttpMethod.Put)
        allowMethod(HttpMethod.Delete)
        allowMethod(HttpMethod.Patch)
        allowHeader(HttpHeaders.Authorization)
        allowHeader(HttpHeaders.ContentType)
        allowHeader("X-User-ID")
        anyHost() // In production, configure this properly
    }
}

fun Application.configureRouting() {
    routing {
        get("/") {
            call.respond(
                ApiResponse(
                    message = "Unhinged Backend API - Production Ready Build Pipeline",
                    timestamp = System.currentTimeMillis()
                )
            )
        }
        
        get("/health") {
            call.respond(
                HealthResponse(
                    status = "healthy",
                    timestamp = System.currentTimeMillis()
                )
            )
        }
        
        // API routes
        route("/api") {
            get("/status") {
                call.respond(
                    StatusResponse(
                        api = "ready",
                        build = "successful",
                        protobuf = "generated",
                        timestamp = System.currentTimeMillis()
                    )
                )
            }

            // Placeholder for multimodal endpoints
            route("/multimodal") {
                get("/health") {
                    call.respond(
                        ServiceHealthResponse(
                            service = "multimodal",
                            status = "ready",
                            architecture = "kotlin-backend-python-grpc",
                            timestamp = System.currentTimeMillis()
                        )
                    )
                }
            }

            // Placeholder for vision endpoints
            route("/vision") {
                get("/health") {
                    call.respond(
                        ServiceHealthResponse(
                            service = "vision",
                            status = "ready",
                            timestamp = System.currentTimeMillis()
                        )
                    )
                }
            }

            // Placeholder for audio endpoints
            route("/audio") {
                get("/health") {
                    call.respond(
                        ServiceHealthResponse(
                            service = "audio",
                            status = "ready",
                            timestamp = System.currentTimeMillis()
                        )
                    )
                }
            }
        }
    }
}
