import React, { useState, useRef } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  Menu,
  MenuItem,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  Send as SendIcon,
  AddCircle as AddCircleIcon,
  InsertDriveFile as InsertDriveFileIcon,
} from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  isLoading?: boolean;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message here...",
  isLoading = false,
}) => {
  const [message, setMessage] = useState('');
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleFileUpload = () => {
    handleMenuClose();
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setUploadError('Please select a PDF file.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      setUploadError('File size exceeds 10MB.');
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', 'http://localhost:2024/api/v1/upload/pdf', true);

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = (event.loaded / event.total) * 100;
          setUploadProgress(percentComplete);
        }
      };

      xhr.onload = () => {
        if (xhr.status === 200) {
          onSendMessage(`Uploaded file: ${file.name}`);
        } else {
          setUploadError(`Upload failed: ${xhr.statusText}`);
        }
        setUploading(false);
      };

      xhr.onerror = () => {
        setUploadError('Upload failed. Please try again.');
        setUploading(false);
      };

      xhr.send(formData); // todo: this will submit the upload right away, but do we want that?
    } catch (error) {
      console.error('Error uploading file:', error);
      setUploadError('Upload failed. Please try again.');
      setUploading(false);
    }
  };

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
          <IconButton
            size="small"
            color="secondary"
            onClick={handleMenuClick}
          >
            <AddCircleIcon fontSize="small" />
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            <MenuItem onClick={handleFileUpload}>
              <InsertDriveFileIcon sx={{ mr: 1 }} />
              Upload PDF
            </MenuItem>
            <MenuItem>
              placeholder1
            </MenuItem>
            <MenuItem>
              placeholder2
            </MenuItem>
          </Menu>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="application/pdf"
            style={{ display: 'none' }}
          />
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={disabled || uploading}
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
            disabled={!message.trim() || disabled || isLoading || uploading}
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
      {uploading && <LinearProgress variant="determinate" value={uploadProgress} sx={{ mt: 1 }} />}
      {uploadError && <Alert severity="error" sx={{ mt: 1 }}>{uploadError}</Alert>}
    </Paper>
  );
};
