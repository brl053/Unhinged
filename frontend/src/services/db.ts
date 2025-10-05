/**
 * Offline Database Service
 * 
 * IndexedDB wrapper using Dexie for offline-first message storage.
 * Provides local caching with sync capabilities to PostgreSQL backend.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import Dexie, { Table } from 'dexie';

// Database entity interfaces
export interface Message {
  id?: number;
  content: string;
  userId: string;
  timestamp: number;
  synced: boolean;
  type?: 'user' | 'assistant';
}

export interface AudioCache {
  id?: number;
  blob: Blob;
  transcript?: string;
  timestamp: number;
  filename?: string;
}

export interface FileCache {
  id?: number;
  file: File;
  uploadStatus: 'pending' | 'uploading' | 'completed' | 'failed';
  uploadProgress: number;
  timestamp: number;
  serverId?: number;
}

// Dexie database class
export class UnhingedDB extends Dexie {
  // Tables
  messages!: Table<Message>;
  audioCache!: Table<AudioCache>;
  fileCache!: Table<FileCache>;

  constructor() {
    super('UnhingedDB');
    
    // Database schema version 1
    this.version(1).stores({
      messages: '++id, userId, timestamp, synced, type',
      audioCache: '++id, timestamp, filename',
      fileCache: '++id, timestamp, uploadStatus'
    });

    // Hooks for data validation
    this.messages.hook('creating', (primKey, obj, trans) => {
      obj.timestamp = obj.timestamp || Date.now();
      obj.synced = obj.synced ?? false;
      obj.type = obj.type || 'user';
    });

    this.audioCache.hook('creating', (primKey, obj, trans) => {
      obj.timestamp = obj.timestamp || Date.now();
    });

    this.fileCache.hook('creating', (primKey, obj, trans) => {
      obj.timestamp = obj.timestamp || Date.now();
      obj.uploadStatus = obj.uploadStatus || 'pending';
      obj.uploadProgress = obj.uploadProgress || 0;
    });
  }
}

// Singleton database instance
export const db = new UnhingedDB();

// Database helper functions
export const dbHelpers = {
  // Message operations
  messages: {
    // Add new message (offline-first)
    add: async (content: string, type: 'user' | 'assistant' = 'user'): Promise<Message> => {
      const message: Message = {
        content,
        userId: 'current-user', // TODO: Replace with actual user ID from auth
        timestamp: Date.now(),
        synced: false,
        type
      };
      
      const id = await db.messages.add(message);
      return { ...message, id };
    },

    // Get all messages ordered by timestamp
    getAll: async (): Promise<Message[]> => {
      return await db.messages.orderBy('timestamp').toArray();
    },

    // Get unsynced messages
    getUnsynced: async (): Promise<Message[]> => {
      return await db.messages.where('synced').equals(0).toArray();
    },

    // Mark messages as synced
    markSynced: async (messageIds: number[]): Promise<void> => {
      await db.messages.bulkUpdate(
        messageIds.map(id => ({ key: id, changes: { synced: true } }))
      );
    },

    // Clear all messages
    clear: async (): Promise<void> => {
      await db.messages.clear();
    }
  },

  // Audio cache operations
  audioCache: {
    // Store audio blob with optional transcript
    store: async (blob: Blob, transcript?: string, filename?: string): Promise<AudioCache> => {
      const audioData: AudioCache = {
        blob,
        transcript,
        filename: filename || `recording-${Date.now()}.webm`,
        timestamp: Date.now()
      };
      
      const id = await db.audioCache.add(audioData);
      return { ...audioData, id };
    },

    // Get recent audio recordings
    getRecent: async (limit: number = 10): Promise<AudioCache[]> => {
      return await db.audioCache
        .orderBy('timestamp')
        .reverse()
        .limit(limit)
        .toArray();
    },

    // Clear old audio cache (older than 24 hours)
    clearOld: async (): Promise<void> => {
      const oneDayAgo = Date.now() - (24 * 60 * 60 * 1000);
      await db.audioCache.where('timestamp').below(oneDayAgo).delete();
    }
  },

  // File cache operations
  fileCache: {
    // Add file to upload queue
    addToQueue: async (file: File): Promise<FileCache> => {
      const fileData: FileCache = {
        file,
        uploadStatus: 'pending',
        uploadProgress: 0,
        timestamp: Date.now()
      };
      
      const id = await db.fileCache.add(fileData);
      return { ...fileData, id };
    },

    // Update upload progress
    updateProgress: async (id: number, progress: number, status?: FileCache['uploadStatus']): Promise<void> => {
      const updates: Partial<FileCache> = { uploadProgress: progress };
      if (status) updates.uploadStatus = status;
      
      await db.fileCache.update(id, updates);
    },

    // Get pending uploads
    getPending: async (): Promise<FileCache[]> => {
      return await db.fileCache.where('uploadStatus').equals('pending').toArray();
    },

    // Mark upload as completed
    markCompleted: async (id: number, serverId: number): Promise<void> => {
      await db.fileCache.update(id, {
        uploadStatus: 'completed',
        uploadProgress: 100,
        serverId
      });
    },

    // Clear completed uploads
    clearCompleted: async (): Promise<void> => {
      await db.fileCache.where('uploadStatus').equals('completed').delete();
    }
  },

  // Database maintenance
  maintenance: {
    // Get database size info
    getSize: async (): Promise<{ messages: number; audioCache: number; fileCache: number }> => {
      const [messages, audioCache, fileCache] = await Promise.all([
        db.messages.count(),
        db.audioCache.count(),
        db.fileCache.count()
      ]);
      
      return { messages, audioCache, fileCache };
    },

    // Clear all data (for testing/reset)
    clearAll: async (): Promise<void> => {
      await Promise.all([
        db.messages.clear(),
        db.audioCache.clear(),
        db.fileCache.clear()
      ]);
    },

    // Export data for backup
    exportData: async (): Promise<{ messages: Message[]; audioCache: AudioCache[] }> => {
      const [messages, audioCache] = await Promise.all([
        db.messages.toArray(),
        db.audioCache.toArray()
      ]);
      
      return { messages, audioCache };
    }
  }
};

// Database initialization
export const initializeDatabase = async (): Promise<void> => {
  try {
    await db.open();
    console.log('✅ IndexedDB initialized successfully');
    
    // Clean up old audio cache on startup
    await dbHelpers.audioCache.clearOld();
    
    // Log database size
    const size = await dbHelpers.maintenance.getSize();
    console.log('📊 Database size:', size);
    
  } catch (error) {
    console.error('❌ Failed to initialize IndexedDB:', error);
    throw error;
  }
};
