from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating a category"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoriesBulkCreate(BaseModel):
    """Schema for creating multiple categories at once"""
    categories: list[CategoryCreate] = Field(..., min_length=1, description="List of categories to create")


class UserCategoryPreferenceUpdate(BaseModel):
    """Schema for updating user category preferences"""
    category_ids: list[int] = Field(..., description="List of category IDs to subscribe to")
