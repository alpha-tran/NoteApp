import React from 'react';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Checkbox,
  IconButton,
  Typography,
  Paper,
  Box
} from '@mui/material';
import { Delete as DeleteIcon } from '@mui/icons-material';
import { useTodoContext } from '../contexts/TodoContext';

export const TodoList: React.FC = () => {
  const { todos, toggleTodo, deleteTodo } = useTodoContext();

  return (
    <Box sx={{ width: '100%', maxWidth: 800, mx: 'auto', mt: 4 }}>
      {todos.length > 0 ? (
        <Paper elevation={2}>
          <List>
            {todos.map((todo) => (
              <ListItem
                key={todo.id}
                secondaryAction={
                  <IconButton edge="end" onClick={() => deleteTodo(todo.id)} color="error">
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemIcon>
                  <Checkbox
                    edge="start"
                    checked={todo.completed}
                    onChange={() => toggleTodo(todo.id)}
                  />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Typography
                      variant="h6"
                      sx={{
                        textDecoration: todo.completed ? 'line-through' : 'none',
                        color: todo.completed ? 'text.secondary' : 'text.primary'
                      }}
                    >
                      {todo.title}
                    </Typography>
                  }
                  secondary={
                    <Typography
                      variant="body2"
                      sx={{
                        color: todo.completed ? 'text.disabled' : 'text.secondary'
                      }}
                    >
                      {todo.description}
                    </Typography>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      ) : (
        <Typography
          variant="body1"
          color="text.secondary"
          align="center"
          sx={{ mt: 4 }}
        >
          No todos yet. Add one to get started!
        </Typography>
      )}
    </Box>
  );
}; 