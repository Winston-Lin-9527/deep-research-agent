import React, { useState, useCallback, useEffect, useRef } from 'react';
import { useStream } from "@langchain/langgraph-sdk/react";
import type { Message } from "@langchain/langgraph-sdk";
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
import type { Conversation, ChatState } from '../types/chat';

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
  const thread = useStream<{
    messages: Message[];
  }>({
    apiUrl: "http://localhost:2024",
    assistantId: "simple_chat",
    messagesKey: "messages",
  });

  // // Append only the latest AI message from the stream into the active conversation
  // useEffect(() => {
  //   if (!chatState.currentConversationId) return;
  //   const count = thread.messages.length;
  //   if (count === 0) return;

  //   const message = thread.messages[count - 1];
  //   const messageId = `${message.type}_${count - 1}_${message.content}`;
  //   if (message.type !== 'ai' || !message.content) return;
  //   if (processedAiIdsRef.current.has(messageId)) return;

  //   const aiMessage: MessageUI = {
  //     id: generateId(),
  //     content: message.content as string,
  //     role: 'assistant',
  //     timestamp: new Date(),
  //   };
  //   // console.log(aiMessage);

  //   setChatState(prev => ({
  //     ...prev,
  //     conversations: prev.conversations.map(conv =>
  //       conv.id === chatState.currentConversationId
  //         ? {
  //             ...conv,
  //             messages: [...conv.messages, aiMessage],
  //             updatedAt: new Date(),
  //           }
  //         : conv
  //     ),
  //     isLoading: false,
  //   }));

  //   processedAiIdsRef.current.add(messageId);
  // }, [thread.messages, chatState.currentConversationId]);
  


  const handleMenuClick = useCallback(() => {
    setSidebarOpen(!sidebarOpen);
    console.log(thread.messages);
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

  const handleSendMessage = (async (content: string) => {
    // const userMessage: MessageUI = {
    //   id: generateId(),
    //   content,
    //   role: 'user',
    //   timestamp: new Date(),
    // };

    // Submit to LangGraph server
    thread.submit({ messages: [{ type: "human", content }] });
    // Create new conversation if none exists
    // let currentConversationId = chatState.currentConversationId;
    // if (!currentConversationId) {
    //   const newConversation: Conversation = {
    //     id: generateId(),
    //     title: content.length > 30 ? content.substring(0, 30) + '...' : content,
    //     messages: [userMessage],
    //     createdAt: new Date(),
    //     updatedAt: new Date(),
    //   };

    //   setChatState(prev => ({
    //     ...prev,
    //     conversations: [newConversation, ...prev.conversations],
    //     currentConversationId: newConversation.id,
    //   }));
    //   currentConversationId = generateId();
    // } else {
    //   // Add message to existing conversation
    //   setChatState(prev => ({
    //     ...prev,
    //     conversations: prev.conversations.map(conv =>
    //       conv.id === currentConversationId
    //         ? {
    //             ...conv,
    //             // messages: [...conv.messages, userMessage],
    //             updatedAt: new Date(),
    //           }
    //         : conv
    //     ),
    //   }));
  });

    // // Simulate AI response
    // setTimeout(() => {
    //   const aiMessage: MessageUI = {
    //     id: generateId(),
    //     content: `This is a simulated response to: "${content}". In a real implementation, this would connect to an AI service like OpenAI's API.`,
    //     role: 'assistant',
    //     timestamp: new Date(),
    //   };

    //   setChatState(prev => ({
    //     ...prev,
    //     conversations: prev.conversations.map(conv =>
    //       conv.id === currentConversationId
    //         ? {
    //             ...conv,
    //             messages: [...conv.messages, aiMessage],
    //             updatedAt: new Date(),
    //           }
    //         : conv
    //     ),
    //     isLoading: false,
    //   }));
    // }, 1500);
  // }, [chatState.currentConversationId]);

  // const currentConversation = chatState.conversations.find(
  //   conv => conv.id === chatState.currentConversationId
  // );

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
              messages={thread.messages || []}
              isLoading={thread.isLoading}
            />

            {/* <div>
              {thread.messages.map((message) => (
                <div key={message.id}>{message.content as string}</div>
              ))}
            </div> */}

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
                disabled={thread.isLoading}
              />
            </Box>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
};

export default ChatApp;
