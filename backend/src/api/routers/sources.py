from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...repositories import SourceRepository
from ...schemas import SourceCreate, SourceUpdate, SourceResponse
from ...api.dependencies import get_db

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=List[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    """List all sources"""
    repo = SourceRepository(db)
    return repo.get_all()


@router.get("/slug/{slug}", response_model=SourceResponse)
def get_source_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get source by slug"""
    repo = SourceRepository(db)
    source = repo.get_by_slug(slug)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with slug '{slug}' not found"
        )
    return source


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: int, db: Session = Depends(get_db)):
    """Get source by ID"""
    repo = SourceRepository(db)
    source = repo.get_by_id(source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID {source_id} not found"
        )
    return source


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """Create a new source"""
    repo = SourceRepository(db)
    
    # Check if URL already exists
    existing = repo.get_by_url(source.url)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source with URL '{source.url}' already exists"
        )
    
    # Check if slug already exists
    existing_slug = repo.get_by_slug(source.slug)
    if existing_slug:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source with slug '{source.slug}' already exists"
        )
    
    new_source = repo.create(name=source.name, url=source.url, slug=source.slug)
    return new_source


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: int,
    source_update: SourceUpdate,
    db: Session = Depends(get_db)
):
    """Update a source"""
    repo = SourceRepository(db)
    
    # Check if source exists
    existing_source = repo.get_by_id(source_id)
    if not existing_source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID {source_id} not found"
        )
    
    # Check if new URL conflicts with another source
    if source_update.url:
        url_source = repo.get_by_url(source_update.url)
        if url_source and url_source.id != source_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"URL '{source_update.url}' is already used by another source"
            )
    
    # Check if new slug conflicts with another source
    if source_update.slug:
        slug_source = repo.get_by_slug(source_update.slug)
        if slug_source and slug_source.id != source_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slug '{source_update.slug}' is already used by another source"
            )
    
    updated_source = repo.update(
        source_id,
        name=source_update.name,
        slug=source_update.slug,
        url=source_update.url
    )
    return updated_source


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(source_id: int, db: Session = Depends(get_db)):
    """Delete a source"""
    repo = SourceRepository(db)
    
    success = repo.delete(source_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source with ID {source_id} not found"
        )

