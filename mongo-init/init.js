db.auth('admin', process.env.MONGO_INITDB_ROOT_PASSWORD);

db = db.getSiblingDB('noteapp');

db.createUser({
    user: process.env.MONGO_INITDB_USERNAME,
    pwd: process.env.MONGO_INITDB_PASSWORD,
    roles: [
        {
            role: 'readWrite',
            db: 'noteapp'
        }
    ]
});

// Create initial collections
db.createCollection('users');
db.createCollection('notes');

// Create indexes
db.users.createIndex({ "email": 1 }, { unique: true });
db.notes.createIndex({ "userId": 1 });
db.notes.createIndex({ "createdAt": 1 }); 