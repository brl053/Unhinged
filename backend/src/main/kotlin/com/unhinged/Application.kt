package com.unhinged

import io.ktor.server.application.*

fun Application.module() {
    configureSerialization()
    configureDatabases()
    configureSockets()
    configureSecurity()
    configureRouting()
}
