# Frontend NoteApp

## Cài đặt

```bash
# Cài đặt dependencies
npm install --legacy-peer-deps
```

## Khởi động ứng dụng

### Sử dụng React Scripts (mặc định)
```bash
npm run dev
# hoặc
npm start
```

### Sử dụng Vite (khuyên dùng cho phát triển)
```bash
npm run dev:vite
```

## Build ứng dụng

```bash
npm run build
```

## Lưu ý về bảo mật

Ứng dụng này đã được cập nhật để khắc phục nhiều lỗ hổng bảo mật trong các dependencies. Chi tiết về các cập nhật bảo mật có thể được tìm thấy trong tệp [SECURITY-UPDATE.md](./SECURITY-UPDATE.md).

## Linting

```bash
# Kiểm tra lỗi
npm run lint

# Tự động sửa lỗi
npm run lint:fix
```

## Công nghệ sử dụng

- React 18
- TypeScript
- Material-UI
- React Router
- Axios
- Vite (cho môi trường phát triển nhanh hơn)
- React Scripts 