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
    // OpenTelemetry for tracing integration
    api("io.opentelemetry:opentelemetry-api:1.30.0")
    api("io.opentelemetry:opentelemetry-sdk:1.30.0")
    
    // YAML processing for structured output
    api("org.yaml:snakeyaml:2.2")
    
    // JSON processing (optional, for JSON output format)
    api("com.fasterxml.jackson.module:jackson-module-kotlin:2.15.2")
    api("com.fasterxml.jackson.datatype:jackson-datatype-jsr310:2.15.2")
    
    // Coroutines for async operations
    api("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    // SLF4J compatibility (optional bridge)
    compileOnly("org.slf4j:slf4j-api:2.0.9")
    
    // Testing
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
    testImplementation("io.opentelemetry:opentelemetry-sdk-testing:1.30.0")
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
                name.set("Unhinged Event Framework - Kotlin")
                description.set("Polyglot event logging framework for Unhinged services with OpenTelemetry integration")
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
