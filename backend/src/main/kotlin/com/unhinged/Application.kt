// ============================================================================
// Unhinged Backend Application - LLM-Native Service Platform
// ============================================================================
//
// @file Application.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-04
// @description Main application entry point with Koin DI and dual protocol support
// ============================================================================

package com.unhinged

import com.unhinged.di.*
import com.unhinged.services.documentstore.DocumentStoreService
import io.grpc.Server
import io.grpc.ServerBuilder
import io.ktor.server.application.*
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import kotlinx.coroutines.*
import org.koin.core.context.GlobalContext.startKoin
import org.koin.core.logger.Level
import org.koin.logger.slf4jLogger
import org.slf4j.LoggerFactory
import kotlin.system.exitProcess

/**
 * Main application entry point with dual protocol support (HTTP + gRPC)
 */
fun main() {
    val logger = LoggerFactory.getLogger("UnhingedApplication")

    try {
        // Initialize dependency injection
        logger.info("Initializing Unhinged Backend Application v1.0.0")
        initializeDependencyInjection()

        // Start both servers
        runBlocking {
            launch { startGrpcServer() }
            launch { startKtorServer() }

            logger.info("All servers started successfully")
            logger.info("HTTP Server: http://localhost:8080")
            logger.info("gRPC Server: localhost:9090")

            // Keep running
            while (true) {
                delay(1000)
            }
        }

    } catch (e: Exception) {
        logger.error("Failed to start application: ${e.message}", e)
        exitProcess(1)
    }
}

/**
 * Initialize Koin dependency injection
 */
private fun initializeDependencyInjection() {
    startKoin {
        slf4jLogger(Level.INFO)
        modules(
            databaseModule,
            cdcModule,
            documentStoreModule
            // TODO: Add other modules as they're implemented
        )
    }
}

/**
 * Start gRPC server with DocumentStore service
 */
private suspend fun startGrpcServer() {
    val logger = LoggerFactory.getLogger("gRPCServer")
    logger.info("Starting gRPC server on port 9090")

    val documentStoreService = org.koin.core.context.GlobalContext.get().get<DocumentStoreService>()

    val server = ServerBuilder.forPort(9090)
        .addService(documentStoreService)
        .build()
        .start()

    logger.info("gRPC server started on port 9090")

    Runtime.getRuntime().addShutdownHook(Thread {
        logger.info("Shutting down gRPC server")
        server.shutdown()
    })

    server.awaitTermination()
}

/**
 * Start Ktor HTTP server
 */
private suspend fun startKtorServer() {
    embeddedServer(Netty, port = 8080, host = "0.0.0.0") {
        module()
    }.start(wait = true)
}

/**
 * Ktor application module configuration
 */
fun Application.module() {
    configureSerialization()
    configureDatabases()
    configureSockets()
    configureSecurity()
    configureRouting()
}
