import React, { useState, useCallback } from 'react';
import {
  Box,
  ThemeProvider,
  createTheme,
  CssBaseline,
} from '@mui/material';
import { ChatHeader } from './ChatHeader';
import { ChatSidebar } from './ChatSidebar';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import type { Conversation, Message, ChatState } from '../types/chat';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

export const ChatApp: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [chatState, setChatState] = useState<ChatState>({
    conversations: [],
    currentConversationId: null,
    isLoading: false,
  });

  const generateId = () => Math.random().toString(36).substr(2, 9);

  const handleMenuClick = useCallback(() => {
    setSidebarOpen(!sidebarOpen);
  }, [sidebarOpen]);

  const handleNewChat = useCallback(() => {
    const newConversation: Conversation = {
      id: generateId(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };

    setChatState(prev => ({
      ...prev,
      conversations: [newConversation, ...prev.conversations],
      currentConversationId: newConversation.id,
    }));
    
    setSidebarOpen(false);
  }, []);

  const handleConversationSelect = useCallback((conversationId: string) => {
    setChatState(prev => ({
      ...prev,
      currentConversationId: conversationId,
    }));
    setSidebarOpen(false);
  }, []);

  const handleDeleteConversation = useCallback((conversationId: string) => {
    setChatState(prev => ({
      ...prev,
      conversations: prev.conversations.filter(conv => conv.id !== conversationId),
      currentConversationId: prev.currentConversationId === conversationId 
        ? (prev.conversations.length > 1 ? prev.conversations[1].id : null)
        : prev.currentConversationId,
    }));
  }, []);

  const handleSendMessage = useCallback(async (content: string) => {
    const userMessage: Message = {
      id: generateId(),
      content,
      role: 'user',
      timestamp: new Date(),
    };

    // Create new conversation if none exists
    let currentConversationId = chatState.currentConversationId;
    if (!currentConversationId) {
      const newConversation: Conversation = {
        id: generateId(),
        title: content.length > 30 ? content.substring(0, 30) + '...' : content,
        messages: [userMessage],
        createdAt: new Date(),
        updatedAt: new Date(),
      };

      setChatState(prev => ({
        ...prev,
        conversations: [newConversation, ...prev.conversations],
        currentConversationId: newConversation.id,
        isLoading: true,
      }));

      currentConversationId = newConversation.id;
    } else {
      // Add message to existing conversation
      setChatState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv =>
          conv.id === currentConversationId
            ? {
                ...conv,
                messages: [...conv.messages, userMessage],
                updatedAt: new Date(),
              }
            : conv
        ),
        isLoading: true,
      }));
    }

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: generateId(),
        content: `This is a simulated response to: "${content}". In a real implementation, this would connect to an AI service like OpenAI's API.`,
        role: 'assistant',
        timestamp: new Date(),
      };

      setChatState(prev => ({
        ...prev,
        conversations: prev.conversations.map(conv =>
          conv.id === currentConversationId
            ? {
                ...conv,
                messages: [...conv.messages, aiMessage],
                updatedAt: new Date(),
              }
            : conv
        ),
        isLoading: false,
      }));
    }, 1500);
  }, [chatState.currentConversationId]);

  const currentConversation = chatState.conversations.find(
    conv => conv.id === chatState.currentConversationId
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
        <ChatHeader
          onMenuClick={handleMenuClick}
          onNewChat={handleNewChat}
        />
        
        <Box sx={{ display: 'flex', flexGrow: 1, overflow: 'hidden' }}>
          <ChatSidebar
            open={sidebarOpen}
            onClose={() => setSidebarOpen(false)}
            conversations={chatState.conversations}
            currentConversationId={chatState.currentConversationId}
            onConversationSelect={handleConversationSelect}
            onDeleteConversation={handleDeleteConversation}
            onNewChat={handleNewChat}
          />
          
          <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
            <MessageList
              messages={currentConversation?.messages || []}
              isLoading={chatState.isLoading}
            />
            
            <Box sx={{ 
              p: 2, 
              display: 'flex', 
              justifyContent: 'center',
              borderTop: '1px solid',
              borderColor: 'divider',
              backgroundColor: 'background.default',
            }}>
              <ChatInput
                onSendMessage={handleSendMessage}
                disabled={chatState.isLoading}
              />
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
};
