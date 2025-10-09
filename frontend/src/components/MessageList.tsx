import React, { useEffect, useRef } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';
import { ChatMessage } from './ChatMessage';
import type { Message } from '../types/chat';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
}

export const MessageList: React.FC<MessageListProps> = ({ messages, isLoading }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <Box
      sx={{
        flexGrow: 1,
        overflowY: 'auto',
        p: 1,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {messages.length === 0 && !isLoading && (
        <Box
          sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            height: '100%',
            textAlign: 'center',
            color: 'text.secondary',
          }}
        >
          <Typography variant="h5" gutterBottom>
            Welcome to ChatGPT Clone
          </Typography>
          <Typography variant="body1">
            Start a conversation by typing a message below
          </Typography>
        </Box>
      )}
      
      {messages.map((message) => (
        <ChatMessage key={message.id} message={message} />
      ))}
      
      {isLoading && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            py: 2,
          }}
        >
          <CircularProgress size={24} />
          <Typography variant="body2" sx={{ ml: 2 }}>
            AI is thinking...
          </Typography>
        </Box>
      )}
      
      <div ref={messagesEndRef} />
    </Box>
  );
};
