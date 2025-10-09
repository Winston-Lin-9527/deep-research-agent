import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Add as AddIcon,
} from '@mui/icons-material';
// import { useStream } from "@langchain/langgraph-sdk/react"
// import type { Message } from "@langchain/langgraph-sdk"

interface ChatHeaderProps {
  onMenuClick: () => void;
  onNewChat: () => void;
  title?: string;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  onMenuClick,
  onNewChat,
  title = "ChatGPT Clone hahah"
}) => {
  return (
    <>
      <AppBar position="static" elevation={1}>
        <Toolbar>
          <IconButton
            edge="start"
            color="inherit"
            aria-label="menu"
            onClick={onMenuClick}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
          
          <IconButton
            color="inherit"
            aria-label="new chat"
            onClick={onNewChat}
          >
            <AddIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
    </>
  );
};
