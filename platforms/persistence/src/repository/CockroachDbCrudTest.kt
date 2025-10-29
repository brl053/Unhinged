//
// @llm-type test
// @llm-does cockroachdb crud operations testing suite
//
package platforms.persistence.repository

import kotlinx.coroutines.runBlocking
import java.time.Instant

/**
 * CockroachDB CRUD Test
 * ====================
 * 
 * Direct testing of CRDB operations.
 * Tests each CRUD operation in isolation.
 */
class CockroachDbCrudTest {
    
    private val crdbCrud = CockroachDbCrud(CrdbConfig())
    
    fun testCreate() = runBlocking {
        val entity = CrdbEntity(
            id = "test_entity_001",
            recordType = "test_record",
            data = """{"name": "Test Entity", "value": 42}""",
            metadata = """{"source": "test", "created_by": "test_user"}""",
            createdAt = Instant.now(),
            updatedAt = Instant.now(),
            version = "1.0"
        )
        
        val result = crdbCrud.create(entity)
        
        when (result) {
            is CrdbResult.Success -> {
                println("✅ CREATE: Successfully created entity with ID: ${result.data}")
            }
            is CrdbResult.Error -> {
                println("❌ CREATE failed: ${result.message}")
            }
        }
    }
    
    fun testRead() = runBlocking {
        // First create an entity
        val entity = CrdbEntity(
            id = "test_entity_002",
            recordType = "test_record",
            data = """{"name": "Read Test Entity", "value": 100}""",
            metadata = """{"source": "read_test"}""",
            createdAt = Instant.now(),
            updatedAt = Instant.now(),
            version = "1.0"
        )
        
        crdbCrud.create(entity)
        
        // Now read it back
        val result = crdbCrud.read("test_entity_002")
        
        when (result) {
            is CrdbResult.Success -> {
                if (result.data != null) {
                    println("✅ READ: Successfully read entity: ${result.data.id}")
                    println("   Data: ${result.data.data}")
                } else {
                    println("❌ READ: Entity not found")
                }
            }
            is CrdbResult.Error -> {
                println("❌ READ failed: ${result.message}")
            }
        }
    }
    
    fun testUpdate() = runBlocking {
        // First create an entity
        val entity = CrdbEntity(
            id = "test_entity_003",
            recordType = "test_record",
            data = """{"name": "Original Entity", "value": 50}""",
            metadata = """{"source": "update_test"}""",
            createdAt = Instant.now(),
            updatedAt = Instant.now(),
            version = "1.0"
        )
        
        crdbCrud.create(entity)
        
        // Update it
        val updates = CrdbEntityUpdate(
            data = """{"name": "Updated Entity", "value": 75}""",
            metadata = """{"source": "update_test", "updated": true}"""
        )
        
        val result = crdbCrud.update("test_entity_003", updates)
        
        when (result) {
            is CrdbResult.Success -> {
                println("✅ UPDATE: Successfully updated entity: ${result.data.id}")
                println("   New data: ${result.data.data}")
            }
            is CrdbResult.Error -> {
                println("❌ UPDATE failed: ${result.message}")
            }
        }
    }
    
    fun testDelete() = runBlocking {
        // First create an entity
        val entity = CrdbEntity(
            id = "test_entity_004",
            recordType = "test_record",
            data = """{"name": "Delete Test Entity", "value": 25}""",
            metadata = """{"source": "delete_test"}""",
            createdAt = Instant.now(),
            updatedAt = Instant.now(),
            version = "1.0"
        )
        
        crdbCrud.create(entity)
        
        // Delete it
        val result = crdbCrud.delete("test_entity_004")
        
        when (result) {
            is CrdbResult.Success -> {
                if (result.data) {
                    println("✅ DELETE: Successfully deleted entity: test_entity_004")
                    
                    // Verify it's gone
                    val readResult = crdbCrud.read("test_entity_004")
                    when (readResult) {
                        is CrdbResult.Success -> {
                            if (readResult.data == null) {
                                println("✅ DELETE verification: Entity no longer exists")
                            } else {
                                println("❌ DELETE verification: Entity still exists")
                            }
                        }
                        is CrdbResult.Error -> {
                            println("❌ Failed to verify deletion: ${readResult.message}")
                        }
                    }
                } else {
                    println("❌ DELETE: Entity not found")
                }
            }
            is CrdbResult.Error -> {
                println("❌ DELETE failed: ${result.message}")
            }
        }
    }
    
    fun testList() = runBlocking {
        // Create multiple entities
        val entities = listOf(
            CrdbEntity(
                id = "list_test_001",
                recordType = "list_test",
                data = """{"name": "List Entity 1", "value": 1}""",
                metadata = """{"source": "list_test"}""",
                createdAt = Instant.now(),
                updatedAt = Instant.now(),
                version = "1.0"
            ),
            CrdbEntity(
                id = "list_test_002",
                recordType = "list_test",
                data = """{"name": "List Entity 2", "value": 2}""",
                metadata = """{"source": "list_test"}""",
                createdAt = Instant.now(),
                updatedAt = Instant.now(),
                version = "1.0"
            ),
            CrdbEntity(
                id = "list_test_003",
                recordType = "list_test",
                data = """{"name": "List Entity 3", "value": 3}""",
                metadata = """{"source": "list_test"}""",
                createdAt = Instant.now(),
                updatedAt = Instant.now(),
                version = "1.0"
            )
        )
        
        // Create all entities
        entities.forEach { entity ->
            crdbCrud.create(entity)
        }
        
        // List entities
        val result = crdbCrud.list(limit = 10, offset = 0)
        
        when (result) {
            is CrdbResult.Success -> {
                println("✅ LIST: Successfully listed ${result.data.size} entities")
                
                // Check that our test entities are in the list
                val testEntityIds = result.data.map { it.id }
                val foundTestEntities = testEntityIds.filter { it.startsWith("list_test_") }
                println("   Found test entities: $foundTestEntities")
            }
            is CrdbResult.Error -> {
                println("❌ LIST failed: ${result.message}")
            }
        }
    }
    
    fun testCount() = runBlocking {
        val result = crdbCrud.count()
        
        when (result) {
            is CrdbResult.Success -> {
                println("✅ COUNT: Total entities in database: ${result.data}")
            }
            is CrdbResult.Error -> {
                println("❌ COUNT failed: ${result.message}")
            }
        }
    }
    
    fun testFullCrudCycle() = runBlocking {
        val entityId = "full_crud_test_001"
        
        println("🚀 Starting Full CRUD Cycle Test...")
        
        // CREATE
        val entity = CrdbEntity(
            id = entityId,
            recordType = "full_crud_test",
            data = """{"name": "Full CRUD Test", "value": 999}""",
            metadata = """{"source": "full_crud_test", "cycle": "create"}""",
            createdAt = Instant.now(),
            updatedAt = Instant.now(),
            version = "1.0"
        )
        
        val createResult = crdbCrud.create(entity)
        when (createResult) {
            is CrdbResult.Success -> println("✅ Full CRUD - CREATE: Entity created")
            is CrdbResult.Error -> {
                println("❌ Full CRUD - CREATE failed: ${createResult.message}")
                return@runBlocking
            }
        }
        
        // READ
        val readResult = crdbCrud.read(entityId)
        when (readResult) {
            is CrdbResult.Success -> {
                if (readResult.data != null) {
                    println("✅ Full CRUD - READ: Entity read successfully")
                } else {
                    println("❌ Full CRUD - READ: Entity not found")
                    return@runBlocking
                }
            }
            is CrdbResult.Error -> {
                println("❌ Full CRUD - READ failed: ${readResult.message}")
                return@runBlocking
            }
        }
        
        // UPDATE
        val updates = CrdbEntityUpdate(
            data = """{"name": "Updated Full CRUD Test", "value": 1000}""",
            metadata = """{"source": "full_crud_test", "cycle": "update"}"""
        )
        
        val updateResult = crdbCrud.update(entityId, updates)
        when (updateResult) {
            is CrdbResult.Success -> {
                println("✅ Full CRUD - UPDATE: Entity updated successfully")
                println("   Updated data: ${updateResult.data.data}")
            }
            is CrdbResult.Error -> {
                println("❌ Full CRUD - UPDATE failed: ${updateResult.message}")
                return@runBlocking
            }
        }
        
        // DELETE
        val deleteResult = crdbCrud.delete(entityId)
        when (deleteResult) {
            is CrdbResult.Success -> {
                if (deleteResult.data) {
                    println("✅ Full CRUD - DELETE: Entity deleted successfully")
                } else {
                    println("❌ Full CRUD - DELETE: Entity not found")
                    return@runBlocking
                }
            }
            is CrdbResult.Error -> {
                println("❌ Full CRUD - DELETE failed: ${deleteResult.message}")
                return@runBlocking
            }
        }
        
        // VERIFY DELETION
        val verifyResult = crdbCrud.read(entityId)
        when (verifyResult) {
            is CrdbResult.Success -> {
                if (verifyResult.data == null) {
                    println("✅ Full CRUD - VERIFY: Entity deletion confirmed")
                } else {
                    println("❌ Full CRUD - VERIFY: Entity still exists after deletion")
                }
            }
            is CrdbResult.Error -> {
                println("❌ Full CRUD - VERIFY failed: ${verifyResult.message}")
            }
        }
        
        println("🎉 Full CRUD cycle completed!")
    }
    
    fun runAllTests() {
        println("🚀 CockroachDB CRUD Tests")
        println("=" * 50)
        
        try {
            testCreate()
            testRead()
            testUpdate()
            testDelete()
            testList()
            testCount()
            testFullCrudCycle()
            
            println("\n🎉 All CRDB CRUD tests completed!")
            
        } catch (e: Exception) {
            println("❌ Test execution failed: ${e.message}")
            e.printStackTrace()
        }
    }
}

fun main() {
    val test = CockroachDbCrudTest()
    test.runAllTests()
}
