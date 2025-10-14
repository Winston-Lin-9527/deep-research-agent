import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Switch,
  FormControlLabel,
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
  simulationMode: boolean;
  onSimulationModeChange: (checked: boolean) => void;
  currentConversationId?: string | null;
}

export const ChatHeader: React.FC<ChatHeaderProps> = ({
  onMenuClick,
  onNewChat,
  title = "ChatGPT Clone hahah",
  simulationMode,
  onSimulationModeChange,
  currentConversationId
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
            {currentConversationId && (
              <Typography variant="caption" sx={{ ml: 2, opacity: 0.7 }}>
                Chat ID: {currentConversationId}
              </Typography>
            )}
          </Typography>

          <FormControlLabel
            control={
              <Switch
                checked={simulationMode}
                onChange={(e) => onSimulationModeChange(e.target.checked)}
                color="secondary"
              />
            }
            label="Simulation Mode"
            sx={{ mr: 2, color: 'white' }}
          />
          
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
