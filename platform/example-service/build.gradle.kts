plugins {
    kotlin("jvm") version "1.9.20"
    application
}

group = "com.unhinged.platform"
version = "1.0.0"

repositories {
    mavenCentral()
}

dependencies {
    // Unhinged Service Framework
    implementation(project(":libs:service-framework:kotlin"))
    
    // Additional dependencies for business logic
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")
    implementation("ch.qos.logback:logback-classic:1.4.11")
    
    // Testing
    testImplementation("org.jetbrains.kotlin:kotlin-test")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")
}

kotlin {
    jvmToolchain(17)
}

application {
    mainClass.set("com.unhinged.platform.example.ExampleServiceKt")
}

tasks.test {
    useJUnitPlatform()
}

tasks.run {
    // Allow running with gradle run
    standardInput = System.`in`
}
