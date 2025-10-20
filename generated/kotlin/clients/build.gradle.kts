// Generated build.gradle.kts for Unhinged Proto Clients (Kotlin)

plugins {
    kotlin("jvm") version "1.9.20"
    id("com.google.protobuf") version "0.9.4"
    `maven-publish`
}

group = "com.unhinged"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // Kotlin
    implementation("org.jetbrains.kotlin:kotlin-stdlib")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    
    // Protobuf and gRPC
    implementation("com.google.protobuf:protobuf-kotlin:3.24.4")
    implementation("io.grpc:grpc-kotlin-stub:1.4.0")
    implementation("io.grpc:grpc-netty-shaded:1.58.0")
    implementation("io.grpc:grpc-protobuf:1.58.0")
    
    // Testing
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("io.grpc:grpc-testing:1.58.0")
}

protobuf {
    protoc {
        artifact = "com.google.protobuf:protoc:3.24.4"
    }
    plugins {
        id("grpc") {
            artifact = "io.grpc:protoc-gen-grpc-java:1.58.0"
        }
        id("grpckt") {
            artifact = "io.grpc:protoc-gen-grpc-kotlin:1.4.0:jdk8@jar"
        }
    }
    generateProtoTasks {
        all().forEach {
            it.plugins {
                id("grpc")
                id("grpckt")
            }
            it.builtins {
                id("kotlin")
            }
        }
    }
}

tasks.test {
    useJUnitPlatform()
}

kotlin {
    jvmToolchain(17)
}

publishing {
    publications {
        create<MavenPublication>("maven") {
            from(components["java"])
            
            pom {
                name.set("Unhinged Proto Clients (Kotlin)")
                description.set("Generated Kotlin protobuf clients for Unhinged platform")
                url.set("https://github.com/unhinged/proto-clients")
                
                licenses {
                    license {
                        name.set("MIT License")
                        url.set("https://opensource.org/licenses/MIT")
                    }
                }
                
                developers {
                    developer {
                        id.set("unhinged-team")
                        name.set("Unhinged Team")
                        email.set("team@unhinged.dev")
                    }
                }
            }
        }
    }
}
