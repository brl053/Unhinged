// ============================================================================
// Persistence Platform - Build Configuration
// ============================================================================
//
// @file build.gradle.kts
// @version 1.0.0
// @author Unhinged Team
// @date 2025-10-19
// @description Gradle build configuration for the Persistence Platform
//
// This build file configures the Kotlin project with all necessary
// dependencies for the multi-database persistence platform including
// database drivers, serialization, coroutines, and API frameworks.
//
// ============================================================================

plugins {
    kotlin("jvm") version "1.9.20"
    kotlin("plugin.serialization") version "1.9.20"
    application
    id("com.github.johnrengelman.shadow") version "8.1.1"
}

group = "com.unhinged"
version = "1.0.0"

repositories {
    mavenCentral()
    maven("https://packages.confluent.io/maven/")
}

dependencies {
    // Kotlin and Coroutines
    implementation("org.jetbrains.kotlin:kotlin-stdlib")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-jdk8:1.7.3")
    
    // Serialization
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-yaml:0.55.0")
    
    // Ktor for REST API
    implementation("io.ktor:ktor-server-core:2.3.5")
    implementation("io.ktor:ktor-server-netty:2.3.5")
    implementation("io.ktor:ktor-server-content-negotiation:2.3.5")
    implementation("io.ktor:ktor-server-cors:2.3.5")
    implementation("io.ktor:ktor-server-rate-limit:2.3.5")
    implementation("io.ktor:ktor-server-call-logging:2.3.5")
    implementation("io.ktor:ktor-server-status-pages:2.3.5")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.5")
    
    // Database Drivers
    // PostgreSQL/CockroachDB
    implementation("org.postgresql:postgresql:42.6.0")
    implementation("com.zaxxer:HikariCP:5.0.1")
    
    // Redis
    implementation("redis.clients:jedis:5.0.2")
    
    // MongoDB
    implementation("org.mongodb:mongodb-driver-kotlin-coroutine:4.11.0")
    
    // Elasticsearch
    implementation("org.elasticsearch.client:elasticsearch-rest-high-level-client:7.17.13")
    implementation("org.elasticsearch.client:elasticsearch-rest-client:7.17.13")
    
    // Cassandra
    implementation("com.datastax.oss:java-driver-core:4.17.0")
    implementation("com.datastax.oss:java-driver-query-builder:4.17.0")
    
    // Neo4j
    implementation("org.neo4j.driver:neo4j-java-driver:5.13.0")
    
    // Weaviate (Vector Database)
    implementation("io.weaviate:client:4.4.0")
    
    // Apache Iceberg for Data Lake
    implementation("org.apache.iceberg:iceberg-core:1.4.2")
    implementation("org.apache.iceberg:iceberg-parquet:1.4.2")
    
    // Configuration and Validation
    implementation("com.fasterxml.jackson.core:jackson-core:2.15.3")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin:2.15.3")
    implementation("com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:2.15.3")
    implementation("com.networknt:json-schema-validator:1.0.87")
    
    // Logging
    implementation("ch.qos.logback:logback-classic:1.4.11")
    implementation("org.slf4j:slf4j-api:2.0.9")
    
    // Metrics and Monitoring
    implementation("io.micrometer:micrometer-core:1.11.5")
    implementation("io.micrometer:micrometer-registry-prometheus:1.11.5")
    
    // Tracing
    implementation("io.opentelemetry:opentelemetry-api:1.31.0")
    implementation("io.opentelemetry:opentelemetry-sdk:1.31.0")
    implementation("io.opentelemetry:opentelemetry-exporter-jaeger:1.31.0")
    
    // gRPC (for future implementation)
    implementation("io.grpc:grpc-kotlin-stub:1.4.0")
    implementation("io.grpc:grpc-netty-shaded:1.58.0")
    implementation("com.google.protobuf:protobuf-kotlin:3.24.4")
    
    // Dependency Injection (Koin)
    implementation("io.insert-koin:koin-core:3.5.0")
    implementation("io.insert-koin:koin-ktor:3.5.0")
    
    // Utilities
    implementation("org.apache.commons:commons-lang3:3.13.0")
    implementation("com.google.guava:guava:32.1.3-jre")
    
    // Testing
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("io.ktor:ktor-server-tests:2.3.5")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
    testImplementation("org.testcontainers:testcontainers:1.19.1")
    testImplementation("org.testcontainers:postgresql:1.19.1")
    testImplementation("org.testcontainers:junit-jupiter:1.19.1")
}

application {
    mainClass.set("com.unhinged.persistence.PersistencePlatformApplicationKt")
}

tasks.test {
    useJUnitPlatform()
}

tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs = listOf("-Xjsr305=strict", "-opt-in=kotlin.RequiresOptIn")
    }
}

// Shadow JAR configuration for creating fat JAR
tasks.shadowJar {
    archiveBaseName.set("persistence-platform")
    archiveClassifier.set("")
    archiveVersion.set("")
    
    // Merge service files for proper dependency injection
    mergeServiceFiles()
    
    // Exclude signature files to avoid security exceptions
    exclude("META-INF/*.SF")
    exclude("META-INF/*.DSA")
    exclude("META-INF/*.RSA")
    
    manifest {
        attributes(
            "Main-Class" to "com.unhinged.persistence.PersistencePlatformApplicationKt",
            "Implementation-Title" to "Unhinged Persistence Platform",
            "Implementation-Version" to project.version,
            "Built-By" to System.getProperty("user.name"),
            "Built-Date" to java.time.Instant.now().toString()
        )
    }
}

// Docker build task
tasks.register("buildDocker") {
    dependsOn("shadowJar")
    
    doLast {
        exec {
            commandLine("docker", "build", "-t", "unhinged/persistence-platform:${project.version}", ".")
        }
    }
}

// Development task to run with auto-reload
tasks.register("dev") {
    dependsOn("classes")
    
    doLast {
        exec {
            commandLine(
                "java",
                "-cp", sourceSets.main.get().runtimeClasspath.asPath,
                "-Dlogback.configurationFile=src/main/resources/logback-dev.xml",
                "com.unhinged.persistence.PersistencePlatformApplicationKt",
                "config/persistence-platform.yaml"
            )
        }
    }
}

// Configuration validation task
tasks.register("validateConfig") {
    doLast {
        val configFile = file("config/persistence-platform.yaml")
        val schemaFile = file("config/schema.json")
        
        if (!configFile.exists()) {
            throw GradleException("Configuration file not found: ${configFile.absolutePath}")
        }
        
        if (!schemaFile.exists()) {
            throw GradleException("Schema file not found: ${schemaFile.absolutePath}")
        }
        
        println("✅ Configuration files found")
        println("📋 Config: ${configFile.absolutePath}")
        println("📐 Schema: ${schemaFile.absolutePath}")
        
        // TODO: Add actual JSON schema validation
        println("⚠️  Schema validation not implemented yet")
    }
}

// Integration test task
tasks.register<Test>("integrationTest") {
    description = "Runs integration tests"
    group = "verification"
    
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    
    useJUnitPlatform {
        includeTags("integration")
    }
    
    shouldRunAfter("test")
}

// Performance test task
tasks.register<Test>("performanceTest") {
    description = "Runs performance tests"
    group = "verification"
    
    testClassesDirs = sourceSets["test"].output.classesDirs
    classpath = sourceSets["test"].runtimeClasspath
    
    useJUnitPlatform {
        includeTags("performance")
    }
    
    // Increase memory for performance tests
    maxHeapSize = "2g"
    
    shouldRunAfter("integrationTest")
}

// Code quality tasks
tasks.register("checkCodeQuality") {
    dependsOn("test", "integrationTest")
    
    doLast {
        println("✅ Code quality checks completed")
    }
}

// Release preparation task
tasks.register("prepareRelease") {
    dependsOn("clean", "checkCodeQuality", "shadowJar", "validateConfig")
    
    doLast {
        println("✅ Release preparation completed")
        println("📦 JAR: ${tasks.shadowJar.get().archiveFile.get().asFile.absolutePath}")
        println("🐳 Docker: Run 'gradle buildDocker' to build container")
    }
}

// Custom source sets for different environments
sourceSets {
    create("integration") {
        kotlin.srcDir("src/integration/kotlin")
        resources.srcDir("src/integration/resources")
        compileClasspath += sourceSets.main.get().output + sourceSets.test.get().output
        runtimeClasspath += sourceSets.main.get().output + sourceSets.test.get().output
    }
}

// Environment-specific configurations
configurations {
    create("integrationImplementation") {
        extendsFrom(configurations.testImplementation.get())
    }
    create("integrationRuntimeOnly") {
        extendsFrom(configurations.testRuntimeOnly.get())
    }
}

// JVM configuration
java {
    sourceCompatibility = JavaVersion.VERSION_17
    targetCompatibility = JavaVersion.VERSION_17
}

// Compiler options
tasks.withType<JavaCompile> {
    options.encoding = "UTF-8"
    options.compilerArgs.addAll(listOf("-Xlint:unchecked", "-Xlint:deprecation"))
}

// JAR manifest
tasks.jar {
    manifest {
        attributes(
            "Implementation-Title" to "Unhinged Persistence Platform",
            "Implementation-Version" to project.version,
            "Implementation-Vendor" to "Unhinged Team"
        )
    }
}

// Resource processing
tasks.processResources {
    filesMatching("**/*.properties") {
        expand(project.properties)
    }
    
    filesMatching("**/*.yaml") {
        expand(project.properties)
    }
}

// Development dependencies for hot reload
configurations.create("developmentOnly")

dependencies {
    "developmentOnly"("org.springframework.boot:spring-boot-devtools:3.1.5")
}

// Custom task for generating API documentation
tasks.register("generateApiDocs") {
    doLast {
        println("📚 Generating API documentation...")
        // TODO: Implement OpenAPI/Swagger documentation generation
        println("⚠️  API documentation generation not implemented yet")
    }
}

// Database migration task
tasks.register("migrateDatabase") {
    doLast {
        println("🗄️ Running database migrations...")
        // TODO: Implement database migration logic
        println("⚠️  Database migration not implemented yet")
    }
}

// Health check task
tasks.register("healthCheck") {
    doLast {
        println("🏥 Running health checks...")
        // TODO: Implement health check logic
        println("⚠️  Health check not implemented yet")
    }
}

// Cleanup task
tasks.register("deepClean") {
    dependsOn("clean")
    
    doLast {
        delete("logs")
        delete("data")
        delete("tmp")
        println("🧹 Deep clean completed")
    }
}
