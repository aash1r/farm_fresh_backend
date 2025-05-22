from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_admin_user
from app.models.user import User
from app.models.product import Product
from app.schemas.product import Product as ProductSchema, ProductCreate, ProductUpdate

router = APIRouter(prefix="/products")

@router.get("/", response_model=List[ProductSchema])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    search: Optional[str] = None,
) -> Any:
    """Retrieve products with optional filtering"""
    query = db.query(Product)
    
    # Apply filters
    if type:
        query = query.filter(Product.type == type)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Product.type.ilike(search_term)) | 
            (Product.variation_name.ilike(search_term))
        )
    
    # Apply pagination
    products = query.offset(skip).limit(limit).all()
    
    return products

@router.get("/{product_id}", response_model=ProductSchema)
def read_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """Get a specific product by id"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

# Admin endpoints
@router.post("/", response_model=ProductSchema)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """Create new product (admin only)"""
    product = Product(
        name=product_in.name,
        price=product_in.price,
        image_url=product_in.image_url,
        type=product_in.type,
        stock=product_in.stock,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.put("/{product_id}", response_model=ProductSchema)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """Update a product (admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update product attributes
    if product_in.name is not None:
        product.name = product_in.name
    if product_in.description is not None:
        product.description = product_in.description
    if product_in.price is not None:
        product.price = product_in.price
    if product_in.image_url is not None:
        product.image_url = product_in.image_url
    if product_in.type is not None:
        product.type = product_in.type
    if product_in.stock is not None:
        product.stock = product_in.stock
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product

@router.delete("/{product_id}", response_model=ProductSchema)
def delete_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
) -> Any:
    """Delete a product (admin only)"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    
    return product
