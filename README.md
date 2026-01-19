# Social Knowledge

Hệ thống tự động thu thập tin tức từ các nguồn báo, tóm tắt bằng AI (Google Gemini), phân loại theo categories, và gửi thông báo đến người dùng qua Discord, Telegram, Slack hoặc các webhook tùy chỉnh.

## 🚀 Tính năng

### Backend
- **Web Crawler**: Tự động crawl tin tức từ các nguồn báo (Thanh Niên, Tuổi Trẻ, RSS feeds)
- **AI Summarization**: Sử dụng Google Gemini để tóm tắt bài báo
- **AI Category Classification**: Tự động phân loại bài báo vào categories phù hợp
- **Multi-channel Notifications**: Gửi thông báo qua Discord, Telegram, Slack
- **User Management**: Quản lý users với Firebase Authentication
- **Category Management**: Quản lý categories và user preferences
- **Scheduled Jobs**: Tự động crawl và xử lý tin tức theo lịch trình

### Frontend
- **Google Authentication**: Đăng nhập bằng Google qua Firebase
- **Dashboard**: Quản lý notification channels và category preferences
- **Category Preferences**: Chọn categories quan tâm để nhận thông báo
- **Modern UI**: Giao diện hiện đại với Tailwind CSS

## 📋 Yêu cầu

- Python 3.11+
- Node.js 18+ (hoặc Bun)
- PostgreSQL 12+
- Firebase Project (cho authentication)
- Google Gemini API Key

## 🛠️ Cài đặt

### Backend

1. **Cài đặt uv** (Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. **Cài đặt dependencies**:
```bash
cd backend
uv sync
```

3. **Cấu hình environment**:
```bash
cp .env.example .env
```

Chỉnh sửa `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/social_knowledge
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
CRAWL_AT_HOURS=8
```

4. **Setup PostgreSQL**:
```bash
createdb social_knowledge
```

5. **Chạy backend**:
```bash
uv run python -m src.app
```

Backend sẽ chạy tại `http://localhost:8000`

### Frontend

1. **Cài đặt dependencies**:
```bash
cd frontend
npm install
# hoặc
bun install
```

2. **Cấu hình environment**:
Tạo file `.env.local`:
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Chạy frontend**:
```bash
npm run dev
# hoặc
bun run dev
```

Frontend sẽ chạy tại `http://localhost:3000`

### API Documentation
Truy cập Swagger UI tại: `http://localhost:8000/docs`

## 🚀 Deployment

### Backend với Docker

```bash
cd backend
./build-docker.sh
docker run -p 8000:8000 --env-file .env social-knowledge
```

### Frontend

```bash
cd frontend
npm run build
npm start
```

## 🔧 Development

### Backend
```bash
# Run application
uv run python -m src.app

# Format code
uv run black src/

# Lint code
uv run ruff check src/
```

### Frontend
```bash
# Development
npm run dev

# Build
npm run build

# Lint
npm run lint
```

## 📄 License

MIT

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

