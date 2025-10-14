import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Box,
  Divider,
  Button,
  IconButton,
} from '@mui/material';
import {
  Delete as DeleteIcon,
} from '@mui/icons-material';
import type { Conversation } from '../types/chat';

interface ChatSidebarProps {
  open: boolean;
  onClose: () => void;
  conversations: Conversation[];
  currentConversationId: string | null;
  onConversationSelect: (conversationId: string) => void;
  onDeleteConversation: (conversationId: string) => void;
  onNewChat: () => void;
}

export const ChatSidebar: React.FC<ChatSidebarProps> = ({
  open,
  onClose,
  conversations,
  currentConversationId,
  onConversationSelect,
  onDeleteConversation,
  onNewChat,
}) => {
  const drawerWidth = 280;

  return (
    <Drawer
      variant="temporary"
      open={open}
      onClose={onClose}
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h6" gutterBottom sx={{ m: 0 }}>
            Conversations
          </Typography>
          <Button variant="contained" size="small" onClick={onNewChat}>
            New Chat
          </Button>
        </Box>
        <Divider sx={{ mb: 2 }} />
        
        <List>
          {conversations.map((conversation) => (
            <ListItem
              key={conversation.id}
              disablePadding
              secondaryAction={
                <IconButton
                  edge="end"
                  aria-label="delete"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conversation.id);
                  }}
                  size="small"
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              }
            >
              <ListItemButton
                selected={conversation.id === currentConversationId}
                onClick={() => onConversationSelect(conversation.id)}
                sx={{
                  borderRadius: 1,
                  mb: 0.5,
                }}
              >
                <ListItemText
                  primary={conversation.title}
                  secondary={conversation.messages.length > 0 
                    ? `${conversation.messages.length} messages`
                    : 'Empty conversation'
                  }
                  primaryTypographyProps={{
                    fontSize: '0.9rem',
                  }}
                  secondaryTypographyProps={{
                    fontSize: '0.75rem',
                  }}
                />
              </ListItemButton>
            </ListItem>
          ))}
          
          {conversations.length === 0 && (
            <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
              No conversations yet. Start a new chat!
            </Typography>
          )}
        </List>
      </Box>
    </Drawer>
  );
};
