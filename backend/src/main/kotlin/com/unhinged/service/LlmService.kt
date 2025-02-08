package com.unhinged.service

import io.ktor.client.*
import io.ktor.client.call.*
import io.ktor.client.request.*
import io.ktor.client.statement.*
import io.ktor.client.engine.cio.*
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import io.ktor.utils.io.*
import kotlinx.serialization.json.*
import io.ktor.utils.io.core.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.io.readByteArray
import kotlinx.serialization.*
import java.time.LocalDateTime


@Serializable
data class LlmRequest(
    val prompt: String,
    val model: String,
    val suffix: String? = null,
    val stream: Boolean = true,
    val options: LlmOptions? = null,
    val format: String? = null,
    val raw: Boolean = false,
    val keep_alive: String? = "5m",
    val context: String? = null
)

@Serializable
data class LlmResponse(
    val model: String,
    val created_at: String,
    val response: String?,
    val done: Boolean,
    val total_duration: Long,
    val load_duration: Long,
    val prompt_eval_count: Int,
    val prompt_eval_duration: Long,
    val eval_count: Int,
    val eval_duration: Long
)

@Serializable
data class LlmOptions(
    val temperature: Double = 0.7,
    val top_k: Int = 50,
    val top_p: Double = 0.9,
    val seed: Int? = null,
    val num_predict: Int = 100
)

object LlmService {
    private val model = "openhermes"
    private val client = HttpClient(CIO) {
        install(ContentNegotiation) { json() }
    }

    @OptIn(InternalAPI::class)
    suspend fun queryLlmStream(prompt: String, options: LlmOptions? = null): String {
        try {
            val ollamaHost = System.getenv("OLLAMA_HOST") ?: "http://localhost:11434"  // Default to localhost if not set

            // Set up the request body
            val requestBody = LlmRequest(
                prompt = prompt,
                model = model,
                options = options
            )

            // Make the API call with stream enabled
            val response: HttpResponse = client.post("$ollamaHost/api/generate") {
                contentType(ContentType.Application.Json)
                setBody(requestBody)
            }

//            response.body()?.use { responseBody ->
//                val source: BufferedSource = responseBody.source()
//                while (!source.exhausted()) {
//                    val line = source.readUtf8Line()
//                    if (line != null) {
//                        val jsonResponse = JSONObject(line)
//                        if (jsonResponse.has("response")) {
//                            onResponse(jsonResponse.getString("response"))
//                        }
//                    }
//                }
//                onComplete()
//            }

            val responseFlow = flow<String> {
//                var generatedText = ""
                val channel: ByteReadChannel = response.content
                try {
                    while (true) {
                        if (channel.availableForRead > 0) {
                            val r = channel.readUTF8Line()?.toGenerateResponse()
                            if (r != null) {
//                                generatedText += r.response
                                emit(r.response)
                            }
                        }
                        if (channel.isClosedForRead) break
                        delay(50) // A small delay to prevent tight looping
                    }
//                    onFinish(generatedText)
                } catch (_: Exception) {
                    // Handle specific exceptions here
                }
            }

            val completeResponse = buildString {
                responseFlow.collect { chunk ->
                    append(chunk)  // Append each emitted string to the result
                }
            }

            println("CompleteResponse: $completeResponse")
            return completeResponse

        } catch (e: Exception) {
           return e.message.toString()
        }
    }
}


val json = Json { ignoreUnknownKeys = true }
@OptIn(ExperimentalSerializationApi::class)
fun String.toGenerateResponse(): GenerateResponse? {
    return try {
        json.decodeFromString(this)
    } catch (e: Exception) {
        null
    }
}


@OptIn(ExperimentalSerializationApi::class)
fun String.toEmbedding(): Embedding? {
    return try {
        json.decodeFromString(this)
    } catch (e: Exception) {
        null
    }
}

@OptIn(ExperimentalSerializationApi::class)
fun String.toModels(): Models? {
    return try {
        json.decodeFromString(this)
    } catch (e: Exception) {
        null
    }
}



@Serializable
data class CompletionRequest(val model: String, val prompt: String, val system: String)

@Serializable
data class GenerateResponse(
    val model: String,
    val created_at: String,
    val response: String,
    val done: Boolean,
    val context: String? = null
)


@Serializable
data class Embedding(val embedding: List<Double>)

@Serializable
data class ChatRequest(
    val model: String,
    val messages: List<Message>
)

@Serializable
data class EmbeddingRequest(
    val model: String,
    val prompt: String
)

@Serializable
data class Message(
    val role: Role,
    val content: String,
    val images: List<String>? = null
)

@Serializable
enum class Role {
    @SerialName("user") USER,
    @SerialName("system") SYSTEM,
    @SerialName("assistant") ASSISTANT
}

@Serializable
data class Models(
    val models: List<Model>
)

@Serializable
data class Model(
    val name: String,
    val modified_at: String,
    val size: Long,
    val digest: String,
    val details: ModelDetail
)

@Serializable
data class ModelDetail(
    val format: String,
    val family: String,
    val families: String?,
    val parameter_size: String,
    val quantization_level: String
)


