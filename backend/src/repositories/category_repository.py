from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..database.models import Category

class CategoryRepository:
    """Repository for Category operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, name: str, slug: str, description: Optional[str] = None) -> Category:
        """Create a new category"""
        category = Category(name=name, slug=slug, description=description)
        self.session.add(category)
        self.session.flush()
        return category
    
    def create_bulk(self, categories_data: List[dict]) -> List[Category]:
        """Create multiple categories at once"""
        categories = []
        for cat_data in categories_data:
            category = Category(
                name=cat_data["name"],
                slug=cat_data["slug"],
                description=cat_data.get("description")
            )
            self.session.add(category)
            categories.append(category)
        self.session.flush()
        return categories
    
    def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.session.get(Category, category_id)
    
    def get_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug"""
        stmt = select(Category).where(Category.slug == slug)
        return self.session.scalar(stmt)
    
    def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name"""
        stmt = select(Category).where(Category.name == name)
        return self.session.scalar(stmt)
    
    def get_all(self) -> List[Category]:
        """Get all categories"""
        stmt = select(Category).order_by(Category.name)
        return list(self.session.scalars(stmt).all())
    
    def get_by_ids(self, category_ids: List[int]) -> List[Category]:
        """Get categories by list of IDs"""
        stmt = select(Category).where(Category.id.in_(category_ids))
        return list(self.session.scalars(stmt).all())
    
    def update(self, category_id: int, name: Optional[str] = None, 
               slug: Optional[str] = None, description: Optional[str] = None) -> Optional[Category]:
        """Update category"""
        category = self.get_by_id(category_id)
        if not category:
            return None
        
        if name is not None:
            category.name = name
        if slug is not None:
            category.slug = slug
        if description is not None:
            category.description = description
        
        self.session.flush()
        return category
    
    def delete(self, category_id: int) -> bool:
        """Delete category by ID"""
        category = self.get_by_id(category_id)
        if not category:
            return False
        
        self.session.delete(category)
        self.session.flush()
        return True
