from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...repositories import CategoryRepository
from ...schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from ...api.dependencies import get_db, get_current_user
from ...database.models import User
from ...schemas.category import UserCategoryPreferenceUpdate, CategoriesBulkCreate
from ...repositories import UserRepository

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """List all categories"""
    repo = CategoryRepository(db)
    return repo.get_all()

@router.post("", response_model=List[CategoryResponse], status_code=status.HTTP_201_CREATED)
def create_categories(categories_data: CategoriesBulkCreate, db: Session = Depends(get_db)):
    """Create multiple categories at once"""
    repo = CategoryRepository(db)
    
    # Validate all categories before creating
    errors = []
    request_names = set()
    request_slugs = set()
    
    # First pass: Check for duplicates within the request
    for idx, category in enumerate(categories_data.categories):
        if category.name in request_names:
            errors.append(f"Category at index {idx}: duplicate name '{category.name}' in request")
        else:
            request_names.add(category.name)
        
        if category.slug in request_slugs:
            errors.append(f"Category at index {idx}: duplicate slug '{category.slug}' in request")
        else:
            request_slugs.add(category.slug)
    
    # Second pass: Check if any name/slug already exists in database
    for idx, category in enumerate(categories_data.categories):
        existing_name = repo.get_by_name(category.name)
        if existing_name:
            errors.append(f"Category at index {idx}: name '{category.name}' already exists in database")
        
        existing_slug = repo.get_by_slug(category.slug)
        if existing_slug:
            errors.append(f"Category at index {idx}: slug '{category.slug}' already exists in database")
    
    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors}
        )
    
    # Prepare data for bulk create
    categories_data_list = [
        {
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description
        }
        for cat in categories_data.categories
    ]
    
    # Create all categories
    new_categories = repo.create_bulk(categories_data_list)
    db.commit()
    
    # Refresh all categories
    for category in new_categories:
        db.refresh(category)
    
    return new_categories

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category"""
    repo = CategoryRepository(db)
    
    category = repo.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    # Check if category has articles
    if category.articles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {len(category.articles)} associated articles"
        )
    
    repo.delete(category_id)
    db.commit()

@router.get("/me", response_model=List[CategoryResponse])
def get_user_category_preferences(
    current_user: User = Depends(get_current_user),
):
    """Get current user's category preferences"""
    return current_user.category_preferences


@router.put("/me", response_model=List[CategoryResponse])
def update_user_category_preferences(
    preferences: UserCategoryPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's category preferences"""
    # Validate that all category IDs exist
    category_repo = CategoryRepository(db)
    categories = category_repo.get_by_ids(preferences.category_ids)
    
    if len(categories) != len(preferences.category_ids):
        found_ids = {c.id for c in categories}
        invalid_ids = set(preferences.category_ids) - found_ids
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid category IDs: {list(invalid_ids)}"
        )
    
    # Update preferences
    user_repo = UserRepository(db)
    updated_user = user_repo.set_category_preferences(current_user.id, preferences.category_ids)
    
    db.commit()
    db.refresh(updated_user)
    
    return updated_user.category_preferences

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """Update a category"""
    repo = CategoryRepository(db)
    
    # Check if category exists
    existing_category = repo.get_by_id(category_id)
    if not existing_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {category_id} not found"
        )
    
    # Check if new name conflicts
    if category_update.name:
        name_category = repo.get_by_name(category_update.name)
        if name_category and name_category.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Name '{category_update.name}' is already used by another category"
            )
    
    # Check if new slug conflicts
    if category_update.slug:
        slug_category = repo.get_by_slug(category_update.slug)
        if slug_category and slug_category.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slug '{category_update.slug}' is already used by another category"
            )
    
    updated_category = repo.update(
        category_id,
        name=category_update.name,
        slug=category_update.slug,
        description=category_update.description
    )
    db.commit()
    db.refresh(updated_category)
    return updated_category