// Create database and application user with restricted permissions
db = db.getSiblingDB('noteapp');

// Create application user with restricted permissions
try {
  db.createUser({
    user: 'noteapp_user',
    pwd: 'noteapp_password',
    roles: [
      { role: 'readWrite', db: 'noteapp' }
    ]
  });
  print('User created successfully!');
} catch (e) {
  print('User creation skipped or failed: ' + e);
}

// Create initial collections
db.createCollection('notes');
db.createCollection('users');

// Add indexes for query optimization
db.users.createIndex({ "email": 1 }, { unique: true });
db.notes.createIndex({ "user_id": 1 });

print('MongoDB initialized successfully!'); 