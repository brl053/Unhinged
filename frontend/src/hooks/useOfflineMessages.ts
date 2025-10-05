/**
 * Offline Messages Hook
 * 
 * Manages offline-first message storage with sync capabilities.
 * Uses Dexie for local storage and React Query for server sync.
 * 
 * @author Augment Agent
 * @version 1.0.0
 */

import { useCallback, useEffect } from 'react';
import { useLiveQuery } from 'dexie-react-hooks';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { dbHelpers, Message } from '@/services/db';
import { api, endpoints } from '@/services/api';

// Hook configuration interface
export interface OfflineMessagesConfig {
  /** Auto-sync interval in milliseconds */
  autoSyncInterval?: number;
  /** Enable auto-sync */
  enableAutoSync?: boolean;
  /** Maximum messages to keep locally */
  maxLocalMessages?: number;
}

// Hook return interface
export interface OfflineMessagesReturn {
  // Message data
  messages: Message[] | undefined;
  unsyncedCount: number;
  
  // Actions
  addMessage: (content: string, type?: 'user' | 'assistant') => Promise<Message>;
  syncMessages: () => void;
  clearMessages: () => void;
  
  // Sync state
  isSyncing: boolean;
  lastSyncTime: number | null;
  syncError: Error | null;
}

// Default configuration
const DEFAULT_CONFIG: Required<OfflineMessagesConfig> = {
  autoSyncInterval: 30000, // 30 seconds
  enableAutoSync: true,
  maxLocalMessages: 1000
};

/**
 * Offline Messages Hook
 * 
 * Provides offline-first message management with automatic sync to backend.
 * Messages are stored locally in IndexedDB and synced to PostgreSQL when online.
 * 
 * @param config - Configuration options
 * @returns Message management controls and state
 * 
 * @example
 * ```tsx
 * const ChatComponent = () => {
 *   const { messages, addMessage, syncMessages, isSyncing } = useOfflineMessages({
 *     autoSyncInterval: 60000, // 1 minute
 *     enableAutoSync: true
 *   });
 *   
 *   const handleSendMessage = async (content: string) => {
 *     await addMessage(content, 'user');
 *   };
 *   
 *   return (
 *     <div>
 *       {messages?.map(msg => (
 *         <div key={msg.id}>{msg.content}</div>
 *       ))}
 *       {isSyncing && <div>Syncing...</div>}
 *     </div>
 *   );
 * };
 * ```
 */
export const useOfflineMessages = (config: OfflineMessagesConfig = {}): OfflineMessagesReturn => {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  const queryClient = useQueryClient();

  // Live query for all messages from IndexedDB
  const messages = useLiveQuery(() => dbHelpers.messages.getAll());
  
  // Live query for unsynced messages count
  const unsyncedMessages = useLiveQuery(() => dbHelpers.messages.getUnsynced());
  const unsyncedCount = unsyncedMessages?.length || 0;

  // Add message mutation (offline-first)
  const { mutateAsync: addMessage } = useMutation({
    mutationFn: async ({ content, type }: { content: string; type: 'user' | 'assistant' }) => {
      console.log('💬 Adding message locally:', { content, type });
      
      const message = await dbHelpers.messages.add(content, type);
      console.log('✅ Message added to IndexedDB:', message);
      
      return message;
    },
    onError: (error) => {
      console.error('❌ Failed to add message locally:', error);
    }
  });

  // Sync messages mutation
  const {
    mutate: syncMessages,
    isPending: isSyncing,
    error: syncError,
    data: lastSyncData
  } = useMutation({
    mutationFn: async (): Promise<{ syncedCount: number; timestamp: number }> => {
      console.log('🔄 Starting message sync...');
      
      const unsynced = await dbHelpers.messages.getUnsynced();
      
      if (unsynced.length === 0) {
        console.log('✅ No messages to sync');
        return { syncedCount: 0, timestamp: Date.now() };
      }

      console.log(`📤 Syncing ${unsynced.length} messages to backend...`);

      try {
        // Send messages to backend (bulk endpoint)
        const response = await api.post(endpoints.messagesBulk, {
          messages: unsynced.map(msg => ({
            content: msg.content,
            userId: msg.userId,
            timestamp: msg.timestamp,
            type: msg.type
          }))
        });

        console.log('✅ Messages synced to backend:', response.data);

        // Mark messages as synced in IndexedDB
        const messageIds = unsynced.map(msg => msg.id!);
        await dbHelpers.messages.markSynced(messageIds);

        console.log('✅ Messages marked as synced locally');

        // Invalidate React Query cache
        queryClient.invalidateQueries({ queryKey: ['messages'] });

        return { syncedCount: unsynced.length, timestamp: Date.now() };

      } catch (error) {
        console.error('❌ Failed to sync messages:', error);
        
        // If it's a network error, don't throw - we'll retry later
        if (error instanceof Error && error.message.includes('Network Error')) {
          console.log('📡 Network error - will retry sync later');
          return { syncedCount: 0, timestamp: Date.now() };
        }
        
        throw error;
      }
    },
    onSuccess: (data) => {
      if (data.syncedCount > 0) {
        console.log(`✅ Successfully synced ${data.syncedCount} messages`);
      }
    },
    onError: (error) => {
      console.error('❌ Message sync failed:', error);
    }
  });

  // Clear all messages
  const { mutate: clearMessages } = useMutation({
    mutationFn: async () => {
      console.log('🗑️ Clearing all messages...');
      await dbHelpers.messages.clear();
      queryClient.invalidateQueries({ queryKey: ['messages'] });
    },
    onSuccess: () => {
      console.log('✅ All messages cleared');
    }
  });

  // Auto-sync effect
  useEffect(() => {
    if (!finalConfig.enableAutoSync) return;

    const interval = setInterval(() => {
      if (unsyncedCount > 0 && !isSyncing) {
        console.log(`⏰ Auto-sync triggered (${unsyncedCount} unsynced messages)`);
        syncMessages();
      }
    }, finalConfig.autoSyncInterval);

    return () => clearInterval(interval);
  }, [finalConfig.enableAutoSync, finalConfig.autoSyncInterval, unsyncedCount, isSyncing, syncMessages]);

  // Cleanup old messages effect
  useEffect(() => {
    if (!messages || messages.length <= finalConfig.maxLocalMessages) return;

    const cleanup = async () => {
      const excessCount = messages.length - finalConfig.maxLocalMessages;
      console.log(`🧹 Cleaning up ${excessCount} old messages...`);
      
      // Keep the most recent messages, remove oldest synced messages
      const oldSyncedMessages = messages
        .filter(msg => msg.synced)
        .slice(0, excessCount);
      
      if (oldSyncedMessages.length > 0) {
        // TODO: Implement bulk delete in dbHelpers
        console.log(`🗑️ Would delete ${oldSyncedMessages.length} old synced messages`);
      }
    };

    cleanup();
  }, [messages, finalConfig.maxLocalMessages]);

  // Network status monitoring
  useEffect(() => {
    const handleOnline = () => {
      console.log('📡 Network connection restored - triggering sync');
      if (unsyncedCount > 0) {
        syncMessages();
      }
    };

    const handleOffline = () => {
      console.log('📡 Network connection lost - operating in offline mode');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [unsyncedCount, syncMessages]);

  // Wrapper for addMessage to match expected signature
  const addMessageWrapper = useCallback(
    async (content: string, type: 'user' | 'assistant' = 'user'): Promise<Message> => {
      return await addMessage({ content, type });
    },
    [addMessage]
  );

  return {
    // Message data
    messages,
    unsyncedCount,
    
    // Actions
    addMessage: addMessageWrapper,
    syncMessages,
    clearMessages,
    
    // Sync state
    isSyncing,
    lastSyncTime: lastSyncData?.timestamp || null,
    syncError
  };
};
