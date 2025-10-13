import React from 'react';
import {
  Box,
  Typography,
  Avatar,
  Paper,
  useTheme,
} from '@mui/material';
import {
  Person as PersonIcon,
  SmartToy as BotIcon,
} from '@mui/icons-material';
import type { Message } from '../types/chat';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const theme = useTheme();
  const isUser = message.role === 'user';

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'flex-start',
        mb: 2,
        px: 2,
        gap: 1,
        justifyContent: isUser ? 'flex-end' : 'flex-start',
      }}
    >
      {!isUser && (
        <Avatar
          sx={{
            bgcolor: theme.palette.secondary.main,
            width: 32,
            height: 32,
            mt: 0.5,
          }}
        >
          <BotIcon />
        </Avatar>
      )}
      <Paper
        elevation={1}
        sx={{
          p: 2,
          maxWidth: '70%',
          backgroundColor: isUser 
            ? theme.palette.primary.light 
            : theme.palette.grey[100],
          color: isUser 
            ? theme.palette.primary.contrastText 
            : theme.palette.text.primary,
          borderRadius: 2,
          flexGrow: isUser ? 0 : 1,
        }}
      >
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {message.content}
        </Typography>
        
        <Typography
          variant="caption"
          sx={{
            display: 'block',
            mt: 1,
            opacity: 0.7,
            fontSize: '0.75rem',
          }}
        >
          {/* {message.timestamp.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
          })} */}
        </Typography>
      </Paper>
      {isUser && (
        <Avatar
          sx={{
            bgcolor: theme.palette.primary.main,
            width: 32,
            height: 32,
            mt: 0.5,
          }}
        >
          <PersonIcon />
        </Avatar>
      )}
    </Box>
  );
};
