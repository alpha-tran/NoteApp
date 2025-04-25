import React from 'react';
import { useTodoContext } from '../contexts/TodoContext';

export const TodoList: React.FC = () => {
  const { todos, toggleTodo, deleteTodo } = useTodoContext();

  return (
    <div className="space-y-4">
      {todos.map((todo) => (
        <div
          key={todo.id}
          className="flex items-center justify-between p-4 bg-white rounded-lg shadow"
        >
          <div className="flex items-center space-x-4">
            <input
              type="checkbox"
              checked={todo.completed}
              onChange={() => toggleTodo(todo.id)}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <div>
              <h3 className={`text-lg font-medium ${todo.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
                {todo.title}
              </h3>
              <p className={`text-sm ${todo.completed ? 'text-gray-400' : 'text-gray-600'}`}>
                {todo.description}
              </p>
            </div>
          </div>
          <button
            onClick={() => deleteTodo(todo.id)}
            className="p-2 text-red-600 hover:text-red-800"
          >
            Delete
          </button>
        </div>
      ))}
      {todos.length === 0 && (
        <p className="text-center text-gray-500">No todos yet. Add one to get started!</p>
      )}
    </div>
  );
}; 