// Tạo database và người dùng ứng dụng với quyền hạn chế
db = db.getSiblingDB('noteapp');

// Tạo người dùng ứng dụng với quyền hạn chế
db.createUser({
  user: 'username',
  pwd: 'password',
  roles: [
    { role: 'readWrite', db: 'noteapp' }
  ]
});

// Tạo collection ban đầu
db.createCollection('notes');
db.createCollection('users');

// Thêm index để tối ưu hóa truy vấn
db.users.createIndex({ "email": 1 }, { unique: true });
db.notes.createIndex({ "user_id": 1 });

print('MongoDB đã được khởi tạo thành công!'); 