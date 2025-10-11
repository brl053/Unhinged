
plugins {
    alias(libs.plugins.kotlin.jvm)
    alias(libs.plugins.ktor)
    alias(libs.plugins.kotlin.plugin.serialization)
    // Temporarily disabled to fix build issues
    // id("com.google.protobuf") version "0.9.4"
}

group = "com.unhinged"
version = "1.0.0"

application {
    mainClass.set("com.unhinged.MinimalApplicationKt")

    val isDevelopment: Boolean = project.ext.has("development")
    applicationDefaultJvmArgs = listOf("-Dio.ktor.development=$isDevelopment")
}

repositories {
    mavenCentral()
}

dependencies {
    // ========================================================================
    // Kotlin Core
    // ========================================================================
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-jdk8:1.7.3")

    // ========================================================================
    // Ktor Server Dependencies (existing HTTP/REST API)
    // ========================================================================
    implementation(libs.ktor.server.core)
    implementation(libs.ktor.server.netty)
    implementation(libs.ktor.server.content.negotiation)
    implementation(libs.ktor.serialization.kotlinx.json)
    implementation(libs.ktor.server.websockets)
    implementation(libs.ktor.server.sessions)
    implementation(libs.ktor.server.config.yaml)
    implementation("io.ktor:ktor-server-cors:2.3.4")

    // ========================================================================
    // Ktor Client Dependencies (for LLM API calls)
    // ========================================================================
    implementation("io.ktor:ktor-client-core:2.3.4")
    implementation("io.ktor:ktor-client-cio:2.3.4")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.4")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.4")

    // ========================================================================
    // gRPC and Protobuf (new DocumentStore service)
    // ========================================================================
    implementation("io.grpc:grpc-kotlin-stub:1.4.0")
    implementation("io.grpc:grpc-netty-shaded:1.59.0")
    implementation("io.grpc:grpc-protobuf:1.59.0")
    implementation("io.grpc:grpc-services:1.59.0")
    implementation("com.google.protobuf:protobuf-kotlin:3.25.1")
    implementation("com.google.protobuf:protobuf-java-util:3.25.1")

    // ========================================================================
    // Dependency Injection - Koin
    // ========================================================================
    implementation("io.insert-koin:koin-core:3.5.3")
    implementation("io.insert-koin:koin-ktor:3.5.3")
    implementation("io.insert-koin:koin-logger-slf4j:3.5.3")

    // ========================================================================
    // Database Dependencies
    // ========================================================================
    implementation(libs.exposed.core)
    implementation(libs.exposed.jdbc)
    implementation(libs.h2)
    implementation(libs.postgresql)
    implementation("com.zaxxer:HikariCP:5.1.0")

    // ========================================================================
    // Event Streaming - Kafka for CDC
    // ========================================================================
    implementation("org.apache.kafka:kafka-clients:3.5.1")

    // ========================================================================
    // Logging
    // ========================================================================
    implementation(libs.logback.classic)
    implementation("net.logstash.logback:logstash-logback-encoder:7.4")

    // ========================================================================
    // Observability - OpenTelemetry and Metrics
    // ========================================================================
    implementation("io.opentelemetry:opentelemetry-api:1.31.0")
    implementation("io.opentelemetry:opentelemetry-sdk:1.31.0")
    implementation("io.opentelemetry:opentelemetry-exporter-otlp:1.31.0")

    // Micrometer for Prometheus metrics
    implementation("io.micrometer:micrometer-registry-prometheus:1.11.5")
    implementation("io.ktor:ktor-server-metrics-micrometer:2.3.6")

    // ========================================================================
    // Configuration
    // ========================================================================
    implementation("com.typesafe:config:1.4.3")

    // ========================================================================
    // Testing Dependencies
    // ========================================================================
    testImplementation(libs.ktor.server.test.host)
    testImplementation(libs.kotlin.test.junit)
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("io.insert-koin:koin-test:3.5.3")
    testImplementation("io.insert-koin:koin-test-junit5:3.5.3")
    testImplementation("io.grpc:grpc-testing:1.59.0")
}

// ========================================================================
// Protobuf Configuration - TEMPORARILY DISABLED
// ========================================================================
/*
protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.25.1"
    }
    plugins {
        create("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-java:1.59.0"
        }
        create("grpckt") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.0:jdk8@jar"
        }
    }
    generateProtoTasks {
        all().forEach {
            it.plugins {
                create("grpc")
                create("grpckt")
            }
            it.builtins {
                create("kotlin")
            }
        }
    }
}

// Configure proto source directories
sourceSets {
    main {
        proto {
            srcDir("../proto")
            exclude("universal_event.proto") // Temporarily exclude to resolve conflicts
        }
        kotlin {
            srcDirs("build/generated/source/proto/main/kotlin")
            srcDirs("build/generated/source/proto/main/grpc")
            srcDirs("build/generated/source/proto/main/grpckt")
        }
    }
}
*/

// ========================================================================
// Kotlin Compilation
// ========================================================================
kotlin {
    jvmToolchain(17)
}