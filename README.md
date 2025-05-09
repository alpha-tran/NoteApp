# User Authentication System

A secure user authentication system built with FastAPI and React.

## Features

- User registration with email validation
- Secure password hashing with bcrypt
- JWT-based authentication
- Protected routes
- Comprehensive test suite
- Docker support
- CI/CD pipeline with Jenkins

## Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run the development server:
```bash
uvicorn app.main:app --reload
```

3. Run tests:
```bash
pytest tests/
```

## API Endpoints

- POST `/auth/register` - Register a new user
- POST `/auth/login` - Login and get JWT token
- GET `/auth/me` - Get current user info
- POST `/auth/logout` - Logout current user

## Docker Build

Build the Docker image:
```bash
docker build -t user-auth-app .
```

Run the container:
```bash
docker run -p 8000:8000 user-auth-app
```

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Email validation
- SQL injection protection
- XSS protection
- CORS middleware
- Rate limiting

## Development

1. Clone the repository
2. Install dependencies
3. Create a `.env` file with required environment variables
4. Run tests before submitting PRs

## CI/CD Pipeline

Dự án này sử dụng Jenkins Pipeline để triển khai quy trình CI/CD hoàn chỉnh. Pipeline bao gồm các giai đoạn:

1. **Environment Validation**: Kiểm tra môi trường CI/CD
2. **Checkout**: Lấy mã nguồn từ kho lưu trữ
3. **Setup Python Environment**: Thiết lập môi trường Python
4. **Security Scan**: Quét các lỗ hổng bảo mật với Bandit, Safety và npm audit
5. **Build Backend & Frontend**: Xây dựng các thành phần ứng dụng
6. **Test Backend & Frontend**: Chạy kiểm thử với báo cáo độ phủ
7. **Code Quality Analysis**: Phân tích chất lượng mã với Codacy
8. **Docker Build and Push**: Đóng gói và đẩy Docker images
9. **Update Kubernetes Manifests**: Cập nhật cấu hình triển khai
10. **Deploy to K8s**: Triển khai ứng dụng lên Kubernetes

Tất cả quy trình được định nghĩa trong tệp `Jenkinsfile` ở thư mục gốc.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

MIT
