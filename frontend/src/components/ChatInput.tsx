import React, { useState } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
} from '@mui/material';
import {
  Send as SendIcon,
} from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message here..."
}) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Paper
      elevation={2}
      sx={{
        p: 1.5,
        borderRadius: 3,
        backgroundColor: 'background.paper',
        maxWidth: '600px',
        width: '100%',
        mx: 'auto',
      }}
    >
      <Box component="form" onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled}
            variant="outlined"
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2,
                fontSize: '0.875rem',
              },
            }}
          />
          
          <IconButton
            type="submit"
            color="primary"
            disabled={!message.trim() || disabled}
            size="small"
            sx={{
              backgroundColor: 'primary.main',
              color: 'white',
              minWidth: '36px',
              height: '36px',
              '&:hover': {
                backgroundColor: 'primary.dark',
              },
              '&:disabled': {
                backgroundColor: 'action.disabledBackground',
                color: 'action.disabled',
              },
            }}
          >
            <SendIcon fontSize="small" />
          </IconButton>
        </Box>
      </Box>
    </Paper>
  );
};
