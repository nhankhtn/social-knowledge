from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database.models import Source

class SourceRepository:
    """Repository for Source operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, name: str, url: str, slug: str) -> Source:
        """Create a new source"""
        source = Source(name=name, slug=slug, url=url)
        self.session.add(source)
        self.session.flush()
        return source
    
    def get_by_id(self, source_id: int) -> Optional[Source]:
        """Get source by ID"""
        return self.session.get(Source, source_id)
    
    def get_by_url(self, url: str) -> Optional[Source]:
        """Get source by URL"""
        stmt = select(Source).where(Source.url == url)
        return self.session.scalar(stmt)
    
    def get_by_slug(self, slug: str) -> Optional[Source]:
        """Get source by slug"""
        stmt = select(Source).where(Source.slug == slug)
        return self.session.scalar(stmt)
    
    def get_all(self) -> List[Source]:
        """Get all sources"""
        stmt = select(Source).order_by(Source.name)
        return list(self.session.scalars(stmt).all())
    
    def update(self, source_id: int, name: Optional[str] = None, slug: Optional[str] = None, url: Optional[str] = None) -> Optional[Source]:
        """Update source"""
        source = self.get_by_id(source_id)
        if not source:
            return None
        
        if name is not None:
            source.name = name
        if slug is not None:
            source.slug = slug
        if url is not None:
            source.url = url
        
        self.session.flush()
        return source
    
    def delete(self, source_id: int) -> bool:
        """Delete source by ID"""
        source = self.get_by_id(source_id)
        if not source:
            return False
        
        self.session.delete(source)
        self.session.flush()
        return True

