package com.unhinged

import com.unhinged.service.LlmService
import io.ktor.http.*
import io.ktor.server.application.*
import io.ktor.server.plugins.cors.routing.*
import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Application.configureRouting() {
    install(CORS) {
        anyHost() // Allows all origins (you can specify specific origins later)
        allowCredentials = true
        allowNonSimpleContentTypes = true
        maxAgeInSeconds = 3600
        allowHeader(HttpHeaders.ContentType) // Allow 'Content-Type' header
        allowMethod(HttpMethod.Post) // Allow 'POST' method
        allowMethod(HttpMethod.Options) // Allow 'OPTIONS' method for preflight
    }

    routing {
        get("/") {
            call.respondText("Hello World!")
        }
        post("/chat") {
            // TODO: Prompt is actually JSON. We need to improve FE/BE connection. Good for PoC.
            val prompt = call.receiveText()
            println("Received prompt: $prompt")
            val response = LlmService.queryLlmStream(prompt)
            call.respondText(response)
        }
    }
}

