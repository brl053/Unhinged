plugins {
    kotlin("jvm") version "1.9.20"
    `java-library`
    `maven-publish`
}

group = "com.unhinged"
version = "1.0.0"

repositories {
    mavenCentral()
    gradlePluginPortal()
}

dependencies {
    // gRPC and Protobuf
    api("io.grpc:grpc-kotlin-stub:1.4.0")
    api("io.grpc:grpc-protobuf:1.58.0")
    api("io.grpc:grpc-netty-shaded:1.58.0")
    api("com.google.protobuf:protobuf-kotlin:3.24.4")
    
    // Coroutines for async operations
    api("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    api("org.jetbrains.kotlinx:kotlinx-coroutines-jdk8:1.7.3")
    
    // Observability
    api("io.micrometer:micrometer-core:1.11.0")
    api("io.micrometer:micrometer-registry-prometheus:1.11.0")
    api("io.opentelemetry:opentelemetry-api:1.30.0")
    api("io.opentelemetry:opentelemetry-sdk:1.30.0")
    
    // Configuration
    api("com.typesafe:config:1.4.2")
    
    // Logging
    api("ch.qos.logback:logback-classic:1.4.11")
    api("net.logstash.logback:logstash-logback-encoder:7.4")
    
    // JSON processing
    api("com.fasterxml.jackson.module:jackson-module-kotlin:2.15.2")
    api("com.fasterxml.jackson.datatype:jackson-datatype-jsr310:2.15.2")
    
    // Testing
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
}

kotlin {
    jvmToolchain(17)
    explicitApi()
}

tasks.test {
    useJUnitPlatform()
}

java {
    withSourcesJar()
    withJavadocJar()
}

publishing {
    publications {
        create<MavenPublication>("maven") {
            from(components["java"])
            
            pom {
                name.set("Unhinged Service Framework")
                description.set("Kotlin service framework for Unhinged platform")
                url.set("https://github.com/brl053/Unhinged")
                
                licenses {
                    license {
                        name.set("MIT")
                        url.set("https://opensource.org/licenses/MIT")
                    }
                }
                
                developers {
                    developer {
                        id.set("unhinged-team")
                        name.set("Unhinged Team")
                    }
                }
            }
        }
    }
}
