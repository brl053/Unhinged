package com.unhinged.service

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.Serializable

@Serializable
data class LlmRequest(val prompt: String)

@Serializable
data class LlmResponse(val response: String)

object LlmService {
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) { json() }
    }

    suspend fun queryLlm(prompt: String): LlmResponse {
        try {
            val ollamaHost = System.getenv("OLLAMA_HOST") ?: "http://localhost:11434"  // Default to localhost if not set

            val response: HttpResponse = client.post("$ollamaHost/api/generate") {
                contentType(ContentType.Application.Json)
                setBody(LlmRequest(prompt))
            }
            return response.body()
        } catch (e: Exception) {
            println(e.toString())
            return LlmResponse(e.message ?: "")
        }
    }
}
