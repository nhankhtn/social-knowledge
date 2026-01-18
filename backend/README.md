# Social Knowledge Backend

Hệ thống tự động thu thập tin tức, tóm tắt bằng AI và gửi thông báo qua Discord.

## Setup

### 1. Cài đặt uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Cài đặt dependencies

```bash
cd backend
uv sync
```

### 3. Cấu hình environment

```bash
cp .env.example .env
# Chỉnh sửa .env với thông tin của bạn:
# - DATABASE_URL: PostgreSQL connection string
# - GEMINI_API_KEY: Google Gemini API key
# - DISCORD_BOT_TOKEN: Discord bot token
# - DISCORD_CHANNEL_ID: Discord channel ID để gửi messages
```

### 4. Setup PostgreSQL

Đảm bảo PostgreSQL đã được cài đặt và chạy:

```bash
# Tạo database
createdb social_knowledge

# Hoặc dùng psql
psql -U postgres -c "CREATE DATABASE social_knowledge;"
```

### 5. Chạy ứng dụng

```bash
# Chạy server (sẽ tự động init database và start scheduler)
uv run python -m src.app

# Hoặc dùng uvicorn trực tiếp
uv run uvicorn src.app:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Quản lý Sources

- `GET /api/sources` - List tất cả sources
- `GET /api/sources/{id}` - Get source by ID
- `POST /api/sources` - Tạo source mới
- `PUT /api/sources/{id}` - Cập nhật source
- `DELETE /api/sources/{id}` - Xóa source

### API Documentation

Truy cập Swagger UI tại: `http://localhost:8000/docs`

### Ví dụ sử dụng API

```bash
# List sources
curl http://localhost:8000/api/sources

# Tạo source mới
curl -X POST http://localhost:8000/api/sources \
  -H "Content-Type: application/json" \
  -d '{"name": "VnExpress", "url": "https://vnexpress.net/rss"}'

# Cập nhật source
curl -X PUT http://localhost:8000/api/sources/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "VnExpress News", "url": "https://vnexpress.net/rss"}'

# Xóa source
curl -X DELETE http://localhost:8000/api/sources/1
```

## Cấu trúc Project

```
backend/
├── src/
│   ├── api/              # FastAPI endpoints
│   │   ├── routers/      # API routes
│   │   ├── schemas.py    # Pydantic schemas
│   │   └── dependencies.py
│   ├── config/           # Configuration
│   ├── database/         # Database models và connection
│   ├── crawler/          # Web crawler
│   ├── ai/               # AI summarization (Gemini)
│   ├── discord/          # Discord bot
│   ├── scheduler/        # Job scheduler
│   └── app.py            # Main application
├── pyproject.toml        # uv project config
└── .env                  # Environment variables
```

## Workflow

1. **Scheduler** chạy job mỗi 8 giờ (có thể config trong `.env`)
2. **Crawler** crawl tin tức từ tất cả sources trong database
3. **AI Service** (Gemini) tóm tắt các bài báo mới
4. **Discord Bot** gửi summaries đến Discord channel

## Database Models

- **Source**: Quản lý các trang báo (url + name)
- **Article**: Lưu các bài báo đã crawl
- **Summary**: Lưu summaries được tạo bởi AI
- **DiscordMessage**: Lưu records của messages đã gửi

## Development

```bash
# Run application
uv run python -m src.app

# Run tests
uv run pytest

# Format code
uv run black src/

# Lint code
uv run ruff check src/
```

## Notes

- Scheduler tự động start khi chạy ứng dụng
- Discord bot sẽ tự động connect khi có token
- Database sẽ tự động được init khi start lần đầu
- Job sẽ chạy mỗi 8 giờ, có thể config trong `.env` với `CRAWL_AT_HOURS`
