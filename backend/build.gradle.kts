
plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.ktor)
    alias(libs.plugins.kotlin.plugin.serialization)
}

group = "com.example"
version = "0.0.1"

application {
    mainClass.set("com.unhinged.MainKt")

    val isDevelopment: Boolean = project.ext.has("development")
    applicationDefaultJvmArgs = listOf("-Dio.ktor.development=$isDevelopment")
}

repositories {
    mavenCentral()
}

dependencies {
    // Ktor Server Dependencies
    implementation(libs.ktor.server.core)
    implementation(libs.ktor.server.netty)
    implementation(libs.ktor.server.content.negotiation)
    implementation(libs.ktor.serialization.kotlinx.json)
    implementation(libs.ktor.server.websockets)
    implementation(libs.ktor.server.sessions)
    implementation(libs.ktor.server.config.yaml)

    // Ktor CORS Plugin Dependency (add this line)
    implementation("io.ktor:ktor-server-cors:2.3.4")

    // Ktor Client Dependencies (NEEDED for LLM API calls)
    implementation("io.ktor:ktor-client-core:2.3.4")  // Core client features
    implementation("io.ktor:ktor-client-cio:2.3.4")   // Non-blocking HTTP client
    implementation("io.ktor:ktor-client-content-negotiation:2.3.4")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.4")

    // Database Dependencies
    implementation(libs.exposed.core)
    implementation(libs.exposed.jdbc)
    implementation(libs.h2)
    implementation(libs.postgresql)

    // Kafka Dependencies for CDC
    implementation("org.apache.kafka:kafka-clients:3.5.1")

    // Logging
    implementation(libs.logback.classic)

    // Testing Dependencies
    testImplementation(libs.ktor.server.test.host)
    testImplementation(libs.kotlin.test.junit)
}