// Generated Kotlin Proto Client Registry
// This file is auto-generated - do not edit manually

package com.unhinged.proto

import io.grpc.ManagedChannel
import io.grpc.ManagedChannelBuilder
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.asExecutor

/**
 * Registry for Unhinged proto clients
 * Provides easy access to all generated gRPC service clients
 */
object ClientRegistry {
    
    /**
     * Create a gRPC channel for the specified endpoint
     */
    fun createChannel(host: String, port: Int, useTls: Boolean = false): ManagedChannel {
        val builder = ManagedChannelBuilder.forAddress(host, port)
        
        if (!useTls) {
            builder.usePlaintext()
        }
        
        return builder
            .executor(Dispatchers.IO.asExecutor())
            .build()
    }
    
    /**
     * Create a gRPC channel with default settings for local development
     */
    fun createLocalChannel(port: Int): ManagedChannel {
        return createChannel("localhost", port, useTls = false)
    }
    
    // Service client factory methods will be added here during generation
    // based on the actual proto service definitions found
}
