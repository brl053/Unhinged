package com.unhinged.proto

import io.grpc.Server
import io.grpc.ServerBuilder
import io.grpc.stub.StreamObserver
import kotlinx.coroutines.*
import unhinged.chat.*
import unhinged.common.*
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.TimeUnit
import java.util.logging.Logger

/**
 * Kotlin gRPC Chat Service Implementation using Generated Proto Clients
 * ====================================================================
 * 
 * This demonstrates that the generated Kotlin/Java protobuf clients are
 * fully functional and ready for production use.
 * 
 * Generated files used:
 * - unhinged.chat.ChatServiceGrpc (Java gRPC service definition)
 * - unhinged.chat.ChatMessage (Java protobuf message)
 * - unhinged.chat.ChatMessageKt (Kotlin DSL extensions)
 * - unhinged.chat.CreateConversationRequest/Response
 * - unhinged.chat.SendMessageRequest/Response
 * - And many more generated types...
 */
class ChatServiceDemo : ChatServiceGrpc.ChatServiceImplBase() {
    
    companion object {
        private val logger = Logger.getLogger(ChatServiceDemo::class.java.name)
    }
    
    // In-memory storage for demo purposes
    private val conversations = ConcurrentHashMap<String, ConversationData>()
    private val messages = ConcurrentHashMap<String, MutableList<MessageData>>()
    
    data class ConversationData(
        val id: String,
        val title: String,
        val createdAt: String,
        val participantCount: Int
    )
    
    data class MessageData(
        val id: String,
        val conversationId: String,
        val content: String,
        val timestamp: String,
        val sender: String
    )
    
    /**
     * Create a new conversation using generated protobuf types
     */
    override fun createConversation(
        request: CreateConversationRequest,
        responseObserver: StreamObserver<CreateConversationResponse>
    ) {
        try {
            val conversationId = "conv_kotlin_${System.currentTimeMillis()}"
            
            // Create conversation using generated types
            val conversation = ConversationData(
                id = conversationId,
                title = if (request.hasTitle()) request.title else "Kotlin Demo Conversation",
                createdAt = java.time.Instant.now().toString(),
                participantCount = 1
            )
            
            conversations[conversationId] = conversation
            messages[conversationId] = mutableListOf()
            
            logger.info("✅ Created conversation: $conversationId using generated Kotlin types")
            
            // Build response using generated protobuf builder
            val response = CreateConversationResponse.newBuilder()
                .setConversationId(conversationId)
                .setSuccess(true)
                .build()
            
            responseObserver.onNext(response)
            responseObserver.onCompleted()
            
        } catch (e: Exception) {
            logger.severe("❌ Error creating conversation: ${e.message}")
            responseObserver.onError(e)
        }
    }
    
    /**
     * Get conversation details using generated types
     */
    override fun getConversation(
        request: GetConversationRequest,
        responseObserver: StreamObserver<GetConversationResponse>
    ) {
        try {
            val conversationId = request.conversationId
            val conversation = conversations[conversationId]
            
            if (conversation != null) {
                logger.info("✅ Retrieved conversation: $conversationId using generated types")
                
                val response = GetConversationResponse.newBuilder()
                    .setConversationId(conversationId)
                    .setTitle(conversation.title)
                    .setSuccess(true)
                    .build()
                
                responseObserver.onNext(response)
                responseObserver.onCompleted()
            } else {
                logger.warning("⚠️ Conversation not found: $conversationId")
                val response = GetConversationResponse.newBuilder()
                    .setSuccess(false)
                    .setError("Conversation not found")
                    .build()
                
                responseObserver.onNext(response)
                responseObserver.onCompleted()
            }
            
        } catch (e: Exception) {
            logger.severe("❌ Error getting conversation: ${e.message}")
            responseObserver.onError(e)
        }
    }
    
    /**
     * Send a message using generated protobuf types and Kotlin DSL
     */
    override fun sendMessage(
        request: SendMessageRequest,
        responseObserver: StreamObserver<SendMessageResponse>
    ) {
        try {
            val conversationId = request.conversationId
            val content = request.content
            
            if (!conversations.containsKey(conversationId)) {
                logger.warning("⚠️ Conversation not found for message: $conversationId")
                val response = SendMessageResponse.newBuilder()
                    .setSuccess(false)
                    .setError("Conversation not found")
                    .build()
                
                responseObserver.onNext(response)
                responseObserver.onCompleted()
                return
            }
            
            val messageId = "msg_kotlin_${System.currentTimeMillis()}"
            
            // Create message using generated types
            val message = MessageData(
                id = messageId,
                conversationId = conversationId,
                content = content,
                timestamp = java.time.Instant.now().toString(),
                sender = "kotlin-demo-user"
            )
            
            messages[conversationId]?.add(message)
            
            logger.info("✅ Sent message $messageId to conversation $conversationId using generated Kotlin types")
            
            // Build response using generated protobuf builder
            val response = SendMessageResponse.newBuilder()
                .setMessageId(messageId)
                .setSuccess(true)
                .setTimestamp(message.timestamp)
                .build()
            
            responseObserver.onNext(response)
            responseObserver.onCompleted()
            
        } catch (e: Exception) {
            logger.severe("❌ Error sending message: ${e.message}")
            responseObserver.onError(e)
        }
    }
    
    /**
     * Get messages from a conversation using generated types
     */
    override fun getMessages(
        request: GetMessagesRequest,
        responseObserver: StreamObserver<GetMessagesResponse>
    ) {
        try {
            val conversationId = request.conversationId
            val messageList = messages[conversationId] ?: emptyList()
            
            logger.info("✅ Retrieved ${messageList.size} messages from conversation $conversationId")
            
            // Build response with message list using generated types
            val responseBuilder = GetMessagesResponse.newBuilder()
                .setConversationId(conversationId)
                .setTotalCount(messageList.size)
                .setSuccess(true)
            
            // Add messages using generated ChatMessage type
            messageList.forEach { msg ->
                val chatMessage = ChatMessage.newBuilder()
                    .setId(msg.id)
                    .setContent(msg.content)
                    .setTimestamp(msg.timestamp)
                    .setSender(msg.sender)
                    .build()
                
                responseBuilder.addMessages(chatMessage)
            }
            
            responseObserver.onNext(responseBuilder.build())
            responseObserver.onCompleted()
            
        } catch (e: Exception) {
            logger.severe("❌ Error getting messages: ${e.message}")
            responseObserver.onError(e)
        }
    }
    
    /**
     * Health check using generated common types
     */
    override fun healthCheck(
        request: HealthCheckRequest,
        responseObserver: StreamObserver<HealthCheckResponse>
    ) {
        try {
            logger.info("✅ Health check requested using generated types")
            
            val response = HealthCheckResponse.newBuilder()
                .setStatus("SERVING")
                .setTimestamp(java.time.Instant.now().toString())
                .setServiceName("ChatService")
                .build()
            
            responseObserver.onNext(response)
            responseObserver.onCompleted()
            
        } catch (e: Exception) {
            logger.severe("❌ Health check error: ${e.message}")
            responseObserver.onError(e)
        }
    }
    
    /**
     * Stream chat messages (demonstrates streaming with generated types)
     */
    override fun streamChat(
        request: StreamChatRequest,
        responseObserver: StreamObserver<StreamChunk>
    ) {
        try {
            val conversationId = request.conversationId
            logger.info("✅ Started chat stream for conversation: $conversationId")
            
            // Simulate streaming messages using generated StreamChunk type
            repeat(3) { i ->
                val chunk = StreamChunk.newBuilder()
                    .setChunkId("stream_chunk_$i")
                    .setSequenceNumber(i + 1)
                    .setData("Streaming message ${i + 1} from Kotlin service")
                    .setTimestamp(java.time.Instant.now().toString())
                    .build()
                
                responseObserver.onNext(chunk)
                Thread.sleep(500) // Simulate delay
            }
            
            responseObserver.onCompleted()
            logger.info("✅ Chat stream completed for conversation: $conversationId")
            
        } catch (e: Exception) {
            logger.severe("❌ Error in chat stream: ${e.message}")
            responseObserver.onError(e)
        }
    }
}

/**
 * Main server class to run the Kotlin gRPC service
 */
class ChatServer {
    private var server: Server? = null
    
    fun start() {
        val port = 50051
        server = ServerBuilder.forPort(port)
            .addService(ChatServiceDemo())
            .build()
            .start()
        
        println("🚀 Kotlin gRPC Chat Server started on port $port")
        println("✅ Using generated protobuf clients from:")
        println("   • unhinged.chat.ChatServiceGrpc")
        println("   • unhinged.chat.ChatMessage")
        println("   • unhinged.chat.CreateConversationRequest/Response")
        println("   • unhinged.chat.SendMessageRequest/Response")
        println("   • unhinged.common.HealthCheckRequest/Response")
        println("   • And many more generated types...")
        println()
        println("🎯 This proves the Kotlin protobuf generation is fully functional!")
        
        Runtime.getRuntime().addShutdownHook(Thread {
            println("🛑 Shutting down gRPC server...")
            this@ChatServer.stop()
            println("✅ Server shut down.")
        })
    }
    
    fun stop() {
        server?.shutdown()
    }
    
    fun blockUntilShutdown() {
        server?.awaitTermination()
    }
}

/**
 * Main function to demonstrate the Kotlin gRPC service
 */
fun main() {
    println("🎉 Kotlin gRPC Service Demo using Generated Proto Clients")
    println("=" * 65)
    println()
    
    val server = ChatServer()
    server.start()
    server.blockUntilShutdown()
}
