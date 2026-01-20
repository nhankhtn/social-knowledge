from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, func, JSON, Table, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Association table for User-Category many-to-many relationship
user_category_preferences = Table(
    'user_category_preferences',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime(timezone=True), server_default=func.now())
)


class Category(Base):
    """Model for article categories"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    articles = relationship("Article", back_populates="category")
    users = relationship("User", secondary=user_category_preferences, back_populates="category_preferences")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class Source(Base):
    """Model for news sources"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), nullable=False, unique=True, index=True)
    url = Column(String(500), nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    articles = relationship("Article", back_populates="source")
    
    def __repr__(self):
        return f"<Source(id={self.id}, name='{self.name}', slug='{self.slug}', url='{self.url}')>"


class Article(Base):
    """Model for crawled articles"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), nullable=False, unique=True, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    published_date = Column(DateTime(timezone=True))
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    
    source = relationship("Source", back_populates="articles")
    category = relationship("Category", back_populates="articles")
    summaries = relationship("Summary", back_populates="article")
    
    def __repr__(self):
        return f"<Article(id={self.id}, title='{self.title[:50]}...', url='{self.url}')>"


class Summary(Base):
    """Model for AI-generated summaries"""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False, index=True)
    summary_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    article = relationship("Article", back_populates="summaries")
    discord_messages = relationship("DiscordMessage", back_populates="summary")
    
    def __repr__(self):
        return f"<Summary(id={self.id}, article_id={self.article_id})>"


class DiscordMessage(Base):
    """Model for sent Discord messages"""
    __tablename__ = "discord_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    summary_id = Column(Integer, ForeignKey("summaries.id"), nullable=False, index=True)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(String(100))
    channel_id = Column(String(100))
    message_id = Column(String(100))
    
    summary = relationship("Summary", back_populates="discord_messages")
    
    def __repr__(self):
        return f"<DiscordMessage(id={self.id}, summary_id={self.summary_id})>"


class User(Base):
    """Model for users"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255))
    photo_url = Column(String(500))
    role = Column(String(20), default="USER", nullable=False)  # USER, ADMIN
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    
    notification_channels = relationship("NotificationChannel", back_populates="user", cascade="all, delete-orphan")
    category_preferences = relationship("Category", secondary=user_category_preferences, back_populates="users")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', firebase_uid='{self.firebase_uid}')>"


class NotificationChannel(Base):
    """Model for user notification channels (webhooks, tokens, etc.)"""
    __tablename__ = "notification_channels"
    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='uq_user_provider'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(50), nullable=False, index=True)  # discord_webhook, telegram_bot, slack_webhook, line_notify, custom, etc.
    name = Column(String(255))  # Optional name for the channel
    
    # Flexible credentials - store as JSON
    credentials = Column(JSON, nullable=False)  
    
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="notification_channels")
    
    def __repr__(self):
        return f"<NotificationChannel(id={self.id}, user_id={self.user_id}, provider='{self.provider}')>"

