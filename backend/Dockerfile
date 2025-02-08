# Use a multi-stage build to reduce final image size
FROM gradle:8-jdk17 AS build
WORKDIR /app

# Install dependencies (curl is for testing from inside container to others)
RUN apt update && apt install -y curl

# Copy Gradle wrapper and build configuration first (improves caching)
COPY gradlew gradlew
COPY gradlew.bat gradlew.bat
COPY gradle/ gradle/
COPY build.gradle.kts settings.gradle.kts gradle.properties ./

# Ensure Gradle wrapper is executable
RUN chmod +x gradlew

# Copy the source code
COPY src ./src

# Build the application (skip tests for faster build)
RUN ./gradlew clean build -x test

# Use a smaller base image for runtime
FROM openjdk:17-jdk-slim
WORKDIR /app

# Copy only the built JAR file from the build stage
COPY --from=build /app/build/libs/*.jar app.jar

# Expose the application port
EXPOSE 8080

# Run the application
CMD ["java", "-jar", "app.jar"]
