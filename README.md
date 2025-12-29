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
CRAWL_INTERVAL_HOURS=8
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

## 📚 Cấu trúc Project

```
social-knowledge/
├── backend/                 # FastAPI backend
│   ├── src/
│   │   ├── api/            # API endpoints và routers
│   │   ├── config/          # Configuration
│   │   ├── database/        # Models, migrations, connection
│   │   ├── repositories/    # Data access layer
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   │   ├── ai/          # AI summarization & classification
│   │   │   ├── crawler/     # Web crawlers
│   │   │   ├── discord/     # Discord bot
│   │   │   ├── notifications/ # Notification sender
│   │   │   └── scheduler/   # Job scheduler
│   │   └── utils/           # Utilities
│   └── pyproject.toml
│
└── frontend/                # Next.js frontend
    └── src/
        ├── app/             # Next.js app directory
        ├── components/       # React components
        ├── hooks/           # Custom hooks
        ├── lib/             # Utilities (API, Firebase)
        ├── store/           # Zustand stores
        ├── types/           # TypeScript types
        └── utils/           # Helper functions
```

## 🔄 Workflow

1. **Crawl**: Scheduler tự động crawl tin tức từ các sources (mỗi 8 giờ)
2. **Summarize & Classify**: AI tóm tắt và phân loại bài báo vào categories
3. **Filter**: Chỉ gửi thông báo cho users có category preferences phù hợp
4. **Notify**: Gửi thông báo qua các channels đã cấu hình (Discord, Telegram, Slack)

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Đăng nhập/Đăng ký với Firebase token
- `GET /api/v1/auth/me` - Lấy thông tin user hiện tại
- `PUT /api/v1/auth/me` - Cập nhật thông tin user

### Sources
- `GET /api/v1/sources` - List tất cả sources
- `POST /api/v1/sources` - Tạo source mới
- `PUT /api/v1/sources/{id}` - Cập nhật source
- `DELETE /api/v1/sources/{id}` - Xóa source

### Categories
- `GET /api/v1/categories` - List tất cả categories
- `POST /api/v1/categories` - Tạo nhiều categories (bulk)
- `GET /api/v1/categories/me` - Lấy categories preferences của user
- `PUT /api/v1/categories/me` - Cập nhật category preferences

### Notifications
- `GET /api/v1/notifications` - List notification channels
- `POST /api/v1/notifications` - Tạo notification channel
- `PUT /api/v1/notifications/{id}` - Cập nhật notification channel
- `DELETE /api/v1/notifications/{id}` - Xóa notification channel

### API Documentation
Truy cập Swagger UI tại: `http://localhost:8000/docs`

## 🗄️ Database Models

- **User**: Thông tin người dùng (Firebase UID, email, display name)
- **Source**: Nguồn tin tức (name, slug, URL)
- **Article**: Bài báo đã crawl (title, content, URL, category_id)
- **Category**: Thể loại bài báo (name, slug, description)
- **Summary**: Tóm tắt bài báo được tạo bởi AI
- **NotificationChannel**: Kênh thông báo của user (Discord, Telegram, Slack)
- **UserCategoryPreferences**: Quan hệ many-to-many giữa User và Category

## 🤖 Supported News Sources

- **Thanh Niên** (thanhnien.vn) - Custom crawler
- **Tuổi Trẻ** (tuoitre.vn) - Custom crawler
- **RSS Feeds** - Generic RSS parser cho các nguồn khác

## 🔔 Notification Channels

- **Discord Webhook**: Gửi qua Discord webhook URL
- **Telegram Bot**: Gửi qua Telegram bot token
- **Slack Webhook**: Gửi qua Slack webhook URL
- **Custom Webhook**: Webhook URL tùy chỉnh

## 🎯 Category System

- Categories được tạo và quản lý bởi admin
- AI tự động phân loại bài báo vào categories phù hợp
- Users chọn categories quan tâm để nhận thông báo
- Chỉ articles có category match với user preferences mới được gửi

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

## 📝 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/social_knowledge
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_PROJECT_ID=your_firebase_project_id
CRAWL_INTERVAL_HOURS=8
SUMMARY_BATCH_SIZE=5
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_FIREBASE_API_KEY=your_api_key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your_project_id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
NEXT_PUBLIC_FIREBASE_APP_ID=your_app_id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🛡️ Security

- Firebase Authentication cho user authentication
- JWT tokens cho API authentication
- CORS được cấu hình cho frontend domains
- Input validation với Pydantic schemas

## 📄 License

MIT

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

