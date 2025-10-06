// ============================================================================
// In-Memory Audio Repository - Infrastructure Layer
// ============================================================================
//
// @file InMemoryAudioRepository.kt
// @version 1.0.0
// @author Unhinged Team
// @date 2025-01-05
// @description In-memory implementation of audio repositories for development
//
// This provides a simple in-memory implementation of the audio repositories
// for development and testing. In production, this would be replaced with
// database-backed implementations.
//
// Clean Architecture:
// - Implements domain repository interfaces
// - No business logic (pure data access)
// - Thread-safe concurrent access
// - Ready to be replaced with database implementation
// ============================================================================

package com.unhinged.infrastructure.audio

import com.unhinged.domain.audio.*
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import java.util.concurrent.ConcurrentHashMap

// ============================================================================
// Audio Repository Implementation
// ============================================================================

/**
 * In-memory implementation of AudioRepository
 * 
 * Thread-safe implementation using ConcurrentHashMap and Mutex for
 * compound operations. Suitable for development and testing.
 */
class InMemoryAudioRepository : AudioRepository {
    
    private val transcriptions = ConcurrentHashMap<String, AudioTranscription>()
    private val syntheses = ConcurrentHashMap<String, AudioSynthesis>()
    private val userTranscriptions = ConcurrentHashMap<String, MutableList<String>>()
    private val userSyntheses = ConcurrentHashMap<String, MutableList<String>>()
    private val mutex = Mutex()
    
    override suspend fun saveTranscription(transcription: AudioTranscription): AudioTranscription {
        return mutex.withLock {
            transcriptions[transcription.id] = transcription
            
            // Update user index
            val userId = extractUserIdFromMetadata(transcription.metadata)
            if (userId != null) {
                userTranscriptions.computeIfAbsent(userId) { mutableListOf() }.add(transcription.id)
            }
            
            transcription
        }
    }
    
    override suspend fun getTranscription(id: String): AudioTranscription? {
        return transcriptions[id]
    }
    
    override suspend fun saveSynthesis(synthesis: AudioSynthesis): AudioSynthesis {
        return mutex.withLock {
            syntheses[synthesis.id] = synthesis
            
            // Update user index (synthesis doesn't have userId directly, would need to be passed)
            // For now, we'll skip user indexing for synthesis
            
            synthesis
        }
    }
    
    override suspend fun getSynthesis(id: String): AudioSynthesis? {
        return syntheses[id]
    }
    
    override suspend fun listTranscriptions(
        userId: String,
        limit: Int,
        offset: Int
    ): List<AudioTranscription> {
        val userTranscriptionIds = userTranscriptions[userId] ?: return emptyList()
        
        return userTranscriptionIds
            .drop(offset)
            .take(limit)
            .mapNotNull { transcriptions[it] }
            .sortedByDescending { it.createdAt }
    }
    
    override suspend fun listSyntheses(
        userId: String,
        limit: Int,
        offset: Int
    ): List<AudioSynthesis> {
        val userSynthesisIds = userSyntheses[userId] ?: return emptyList()
        
        return userSynthesisIds
            .drop(offset)
            .take(limit)
            .mapNotNull { syntheses[it] }
            .sortedByDescending { it.createdAt }
    }
    
    override suspend fun deleteTranscription(id: String): Boolean {
        return mutex.withLock {
            val transcription = transcriptions.remove(id)
            if (transcription != null) {
                // Remove from user index
                val userId = extractUserIdFromMetadata(transcription.metadata)
                if (userId != null) {
                    userTranscriptions[userId]?.remove(id)
                }
                true
            } else {
                false
            }
        }
    }
    
    override suspend fun deleteSynthesis(id: String): Boolean {
        return syntheses.remove(id) != null
    }
    
    /**
     * Extracts user ID from STT metadata (helper function)
     */
    private fun extractUserIdFromMetadata(metadata: STTMetadata): String? {
        // This is a placeholder - in real implementation, we'd have user context
        // For now, return null as we don't have user ID in the metadata
        return null
    }
}

// ============================================================================
// Voice Repository Implementation
// ============================================================================

/**
 * In-memory implementation of VoiceRepository
 * 
 * Pre-populated with some default voices for development.
 */
class InMemoryVoiceRepository : VoiceRepository {
    
    private val voices = ConcurrentHashMap<String, Voice>()
    private val mutex = Mutex()
    
    init {
        // Pre-populate with some default voices
        val defaultVoices = listOf(
            Voice(
                id = "voice-en-us-female-1",
                name = "Emma",
                displayName = "Emma (US English)",
                description = "A friendly female voice with American English accent",
                language = "English",
                languageCode = "en-US",
                gender = VoiceGender.FEMALE,
                age = VoiceAge.YOUNG_ADULT,
                style = VoiceStyle.FRIENDLY,
                supportedFormats = listOf(AudioFormat.MP3, AudioFormat.WAV, AudioFormat.OGG),
                supportedSampleRates = listOf(16000, 22050, 44100),
                isAvailable = true,
                isPremium = false,
                costPerCharacter = 0.001f,
                previewText = "Hello! I'm Emma, your friendly voice assistant."
            ),
            Voice(
                id = "voice-en-us-male-1",
                name = "James",
                displayName = "James (US English)",
                description = "A professional male voice with American English accent",
                language = "English",
                languageCode = "en-US",
                gender = VoiceGender.MALE,
                age = VoiceAge.ADULT,
                style = VoiceStyle.PROFESSIONAL,
                supportedFormats = listOf(AudioFormat.MP3, AudioFormat.WAV, AudioFormat.OGG),
                supportedSampleRates = listOf(16000, 22050, 44100),
                isAvailable = true,
                isPremium = false,
                costPerCharacter = 0.001f,
                previewText = "Good day! I'm James, ready to assist you professionally."
            ),
            Voice(
                id = "voice-en-gb-female-1",
                name = "Sophie",
                displayName = "Sophie (British English)",
                description = "An elegant female voice with British English accent",
                language = "English",
                languageCode = "en-GB",
                gender = VoiceGender.FEMALE,
                age = VoiceAge.ADULT,
                style = VoiceStyle.CONVERSATIONAL,
                supportedFormats = listOf(AudioFormat.MP3, AudioFormat.WAV, AudioFormat.FLAC),
                supportedSampleRates = listOf(22050, 44100, 48000),
                isAvailable = true,
                isPremium = true,
                costPerCharacter = 0.002f,
                previewText = "Hello there! I'm Sophie, speaking with a lovely British accent."
            )
        )
        
        defaultVoices.forEach { voice ->
            voices[voice.id] = voice
        }
    }
    
    override suspend fun saveVoice(voice: Voice): Voice {
        return mutex.withLock {
            voices[voice.id] = voice
            voice
        }
    }
    
    override suspend fun getVoice(id: String): Voice? {
        return voices[id]
    }
    
    override suspend fun listVoices(
        language: String?,
        gender: VoiceGender?,
        style: VoiceStyle?,
        premiumOnly: Boolean,
        limit: Int,
        offset: Int
    ): List<Voice> {
        return voices.values
            .filter { voice ->
                (language == null || voice.language.contains(language, ignoreCase = true)) &&
                (gender == null || voice.gender == gender) &&
                (style == null || voice.style == style) &&
                (!premiumOnly || voice.isPremium) &&
                voice.isAvailable
            }
            .sortedBy { it.displayName }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun searchVoices(query: String, limit: Int): List<Voice> {
        val searchQuery = query.lowercase()
        return voices.values
            .filter { voice ->
                voice.isAvailable && (
                    voice.name.lowercase().contains(searchQuery) ||
                    voice.displayName.lowercase().contains(searchQuery) ||
                    voice.description.lowercase().contains(searchQuery) ||
                    voice.language.lowercase().contains(searchQuery)
                )
            }
            .sortedBy { it.displayName }
            .take(limit)
    }
    
    override suspend fun updateVoiceAvailability(id: String, isAvailable: Boolean): Boolean {
        return mutex.withLock {
            val voice = voices[id]
            if (voice != null) {
                voices[id] = voice.copy(isAvailable = isAvailable)
                true
            } else {
                false
            }
        }
    }
    
    override suspend fun deleteVoice(id: String): Boolean {
        return voices.remove(id) != null
    }
}

// ============================================================================
// Audio Session Repository Implementation
// ============================================================================

/**
 * In-memory implementation of AudioSessionRepository
 */
class InMemoryAudioSessionRepository : AudioSessionRepository {
    
    private val sessions = ConcurrentHashMap<String, AudioSession>()
    private val userSessions = ConcurrentHashMap<String, MutableList<String>>()
    private val mutex = Mutex()
    
    override suspend fun createSession(session: AudioSession): AudioSession {
        return mutex.withLock {
            sessions[session.id] = session
            
            // Update user index
            userSessions.computeIfAbsent(session.userId) { mutableListOf() }.add(session.id)
            
            session
        }
    }
    
    override suspend fun getSession(id: String): AudioSession? {
        return sessions[id]
    }
    
    override suspend fun updateSessionStatus(id: String, status: AudioSessionStatus): Boolean {
        return mutex.withLock {
            val session = sessions[id]
            if (session != null) {
                sessions[id] = session.copy(
                    status = status,
                    updatedAt = java.time.Instant.now()
                )
                true
            } else {
                false
            }
        }
    }
    
    override suspend fun listUserSessions(
        userId: String,
        sessionType: AudioSessionType?,
        limit: Int,
        offset: Int
    ): List<AudioSession> {
        val userSessionIds = userSessions[userId] ?: return emptyList()
        
        return userSessionIds
            .mapNotNull { sessions[it] }
            .filter { session ->
                sessionType == null || session.sessionType == sessionType
            }
            .sortedByDescending { it.createdAt }
            .drop(offset)
            .take(limit)
    }
    
    override suspend fun deleteSession(id: String): Boolean {
        return mutex.withLock {
            val session = sessions.remove(id)
            if (session != null) {
                // Remove from user index
                userSessions[session.userId]?.remove(id)
                true
            } else {
                false
            }
        }
    }
}
