# Kiến trúc và Kế hoạch Phát triển - Social Knowledge System

## 1. Tổng quan Hệ thống

Hệ thống tự động thu thập tin tức từ các trang báo, tóm tắt bằng AI và gửi thông báo qua Discord.

### Luồng hoạt động:
```
Cron Job (8h/lần) → Crawler → AI Summary → Discord Bot → Users
```

## 2. Kiến trúc Hệ thống

### 2.1. Kiến trúc Tổng thể

```
┌─────────────────┐
│   Cron Scheduler │  (APScheduler hoặc system cron)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Crawler Service│  (Scrapy/BeautifulSoup/Requests)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Data Storage  │  (SQLite/PostgreSQL - lưu articles đã crawl)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   AI Service     │  (OpenAI API / Anthropic / Local LLM)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Discord Bot   │  (discord.py)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Users       │
└─────────────────┘
```

### 2.2. Components Chi tiết

#### A. Crawler Module
- **Chức năng**: Thu thập tin tức từ các trang báo
- **Input**: Danh sách URLs/feeds RSS
- **Output**: Raw article data (title, content, url, date)
- **Công nghệ**: 
  - `requests` + `BeautifulSoup4` cho HTML parsing
  - `feedparser` cho RSS feeds
  - `scrapy` (optional) cho complex sites

#### B. Data Storage Module
- **Chức năng**: Lưu trữ articles, tránh duplicate
- **Schema**:
  - `articles`: id, url, title, content, published_date, crawled_at
  - `summaries`: id, article_id, summary_text, created_at
  - `discord_messages`: id, summary_id, sent_at, user_id
- **Công nghệ**: SQLite (dev) hoặc PostgreSQL (production)

#### C. AI Summary Module
- **Chức năng**: Tóm tắt nội dung bài báo
- **Input**: Article content
- **Output**: Summary text
- **Công nghệ**: 
  - Google Gemini API (`google-generativeai` package)

#### D. Discord Bot Module
- **Chức năng**: Gửi thông báo tóm tắt đến users
- **Input**: Summary text + metadata
- **Output**: Discord message
- **Công nghệ**: `discord.py`

#### E. Scheduler Module
- **Chức năng**: Chạy job mỗi 8 giờ
- **Công nghệ**: 
  - `APScheduler` (Python-based)
  - Hoặc system cron + Python script

## 3. Technology Stack

### Core Dependencies
```python
# Package Manager
uv (Python package manager)

# Web scraping
requests>=2.31.0
beautifulsoup4>=4.12.0
feedparser>=6.0.10
lxml>=4.9.0

# Database
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0  # PostgreSQL driver

# AI Service
google-generativeai>=0.3.0  # Gemini API

# Discord
discord.py>=2.3.0

# Scheduler
APScheduler>=3.10.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

## 4. Cấu trúc Project

```
social-knowledge/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py                 # Entry point
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py         # Configuration management
│   │   │   └── constants.py        # Constants
│   │   ├── crawler/
│   │   │   ├── __init__.py
│   │   │   ├── base_crawler.py     # Base crawler class
│   │   │   ├── news_sites/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── vnexpress.py
│   │   │   │   ├── dantri.py
│   │   │   │   └── ...             # Các site cụ thể
│   │   │   └── rss_parser.py       # RSS feed parser
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy models
│   │   │   ├── connection.py       # DB connection
│   │   │   └── repository.py       # Data access layer
│   │   ├── ai/
│   │   │   ├── __init__.py
│   │   │   ├── summarizer.py       # AI summarization service
│   │   │   └── providers/
│   │   │       ├── __init__.py
│   │   │       ├── openai_provider.py
│   │   │       └── anthropic_provider.py
│   │   ├── discord/
│   │   │   ├── __init__.py
│   │   │   ├── bot.py              # Discord bot client
│   │   │   └── message_formatter.py # Format messages
│   │   ├── scheduler/
│   │   │   ├── __init__.py
│   │   │   └── job_scheduler.py    # APScheduler setup
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py            # Logging setup
│   │       └── helpers.py           # Helper functions
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_crawler.py
│   │   ├── test_ai.py
│   │   └── test_discord.py
│   ├── pyproject.toml          # uv project configuration
│   ├── .env.example
│   ├── cli.py                  # CLI tool để quản lý sources
│   └── README.md
├── REQUIREMENT.md
└── ARCHITECTURE.md
```

## 5. Kế hoạch Phát triển

### Phase 1: Setup & Infrastructure (Ngày 1-2)
- [ ] Setup project structure
- [ ] Cấu hình environment variables (.env)
- [ ] Setup database models và connection
- [ ] Setup logging system
- [ ] Viết unit tests cơ bản

### Phase 2: Crawler Module (Ngày 3-4)
- [ ] Implement base crawler class
- [ ] Implement crawler cho 2-3 trang báo phổ biến
- [ ] Implement RSS parser
- [ ] Test crawler với các sites khác nhau
- [ ] Implement duplicate detection

### Phase 3: AI Summary Module (Ngày 5-6)
- [ ] Setup AI provider (OpenAI/Anthropic)
- [ ] Implement summarization service
- [ ] Test với các bài báo mẫu
- [ ] Optimize prompt engineering
- [ ] Handle rate limiting và error cases

### Phase 4: Discord Bot Module (Ngày 7-8)
- [ ] Setup Discord bot application
- [ ] Implement bot client với discord.py
- [ ] Implement message formatting
- [ ] Test gửi message
- [ ] Implement user management (nếu cần)

### Phase 5: Scheduler & Integration (Ngày 9-10)
- [ ] Setup APScheduler
- [ ] Implement main job workflow
- [ ] Integrate tất cả modules
- [ ] Error handling và retry logic
- [ ] Monitoring và alerting

### Phase 6: Testing & Deployment (Ngày 11-12)
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Setup production environment
- [ ] Deploy và monitor
- [ ] Documentation

## 6. Chi tiết Implementation

### 6.1. Configuration Management

```python
# config/settings.py structure
- DATABASE_URL
- AI_PROVIDER (openai/anthropic)
- AI_API_KEY
- DISCORD_BOT_TOKEN
- DISCORD_CHANNEL_ID
- CRAWL_INTERVAL_HOURS (8)
- NEWS_SOURCES (list of URLs/RSS feeds)
```

### 6.2. Database Schema

```sql
-- Sources table (quản lý các trang báo)
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Articles table
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    published_date TIMESTAMP,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_id INTEGER REFERENCES sources(id)
);

-- Summaries table
CREATE TABLE summaries (
    id SERIAL PRIMARY KEY,
    article_id INTEGER REFERENCES articles(id),
    summary_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Discord messages table
CREATE TABLE discord_messages (
    id SERIAL PRIMARY KEY,
    summary_id INTEGER REFERENCES summaries(id),
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(100),
    channel_id VARCHAR(100)
);
```

### 6.3. Main Workflow

```python
# Pseudo-code cho main job
def main_job():
    1. Crawl news từ các sources
    2. Filter articles mới (chưa có trong DB)
    3. Với mỗi article mới:
       a. Gọi AI service để summary
       b. Lưu summary vào DB
       c. Format message
       d. Gửi qua Discord
    4. Log kết quả
    5. Handle errors
```

### 6.4. Error Handling Strategy

- **Crawler errors**: Retry 3 lần, skip nếu fail
- **AI API errors**: Retry với exponential backoff
- **Discord errors**: Queue messages, retry sau
- **Database errors**: Log và alert

## 7. Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/social_knowledge

# AI Service - Gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Discord
DISCORD_BOT_TOKEN=...
DISCORD_CHANNEL_ID=...

# Scheduler
CRAWL_INTERVAL_HOURS=8
TIMEZONE=Asia/Ho_Chi_Minh

# News Sources (JSON array)
NEWS_SOURCES=["https://vnexpress.net/rss", "https://dantri.com.vn/rss"]
```

## 8. Deployment Options

### Option 1: Local Server
- Chạy Python script với systemd service
- Sử dụng system cron hoặc APScheduler

### Option 2: Cloud (AWS/GCP/Azure)
- EC2/Compute Engine instance
- RDS/Cloud SQL cho database
- Lambda/Cloud Functions (nếu muốn serverless)

### Option 3: Docker
- Containerize application
- Docker Compose với PostgreSQL
- Cron job trong container

## 9. Monitoring & Logging

- **Logging**: Python logging module với file rotation
- **Metrics**: Track số articles crawled, summaries created, messages sent
- **Alerts**: Email/Discord notification khi có lỗi nghiêm trọng

## 10. Security Considerations

- Store API keys trong environment variables
- Validate và sanitize crawled content
- Rate limiting cho API calls
- Secure database connection
- Discord bot permissions (chỉ gửi message, không cần admin)

## 11. Future Enhancements

- [ ] Support nhiều AI providers
- [ ] User preferences (topics, frequency)
- [ ] Web dashboard để quản lý
- [ ] Multi-language support
- [ ] Caching mechanism
- [ ] Analytics và reporting

