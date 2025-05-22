# import logging
# from sqlalchemy.orm import Session

# from app.core.security import get_password_hash
# from app.models.user import User
# from app.models.product import Product
# from app.core.config import settings

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Initial products
# INITIAL_PRODUCTS = [
#     {
#         "name": "Chaunsa Mango",
#         "description": "Sweet and aromatic Chaunsa mangoes from Punjab, Pakistan",
#         "price": 12.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/chaunsa_mango.jpg",
#         "type": "Chaunsa"
#     },
#     {
#         "name": "Sindhri Mango",
#         "description": "Large, sweet Sindhri mangoes from Sindh, Pakistan",
#         "price": 14.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/sindhri_mango.jpg",
#         "type": "Sindhri"
#     },
#     {
#         "name": "Anwar Ratol Mango",
#         "description": "Small, extremely sweet Anwar Ratol mangoes",
#         "price": 16.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/anwar_ratol_mango.jpg",
#         "type": "Anwar Ratol"
#     },
#     {
#         "name": "Langra Mango",
#         "description": "Fiber-free, sweet Langra mangoes",
#         "price": 13.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/langra_mango.jpg",
#         "type": "Langra"
#     },
#     {
#         "name": "Dussehri Mango",
#         "description": "Thin-skinned, fiber-free Dussehri mangoes",
#         "price": 15.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/dussehri_mango.jpg",
#         "type": "Dussehri"
#     },
#     {
#         "name": "White Chaunsa Mango",
#         "description": "Premium white Chaunsa mangoes with a unique flavor profile",
#         "price": 17.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/white_chaunsa_mango.jpg",
#         "type": "White Chaunsa"
#     },
#     {
#         "name": "Fajri Mango",
#         "description": "Rare Fajri mangoes with a distinctive taste",
#         "price": 18.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/fajri_mango.jpg",
#         "type": "Fajri"
#     },
#     {
#         "name": "Neelum Mango",
#         "description": "Sweet and juicy Neelum mangoes",
#         "price": 13.49,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/neelum_mango.jpg",
#         "type": "Neelum"
#     },
#     {
#         "name": "Alphonso Mango",
#         "description": "Premium Alphonso mangoes, known as the king of mangoes",
#         "price": 19.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/alphonso_mango.jpg",
#         "type": "Alphonso"
#     },
#     {
#         "name": "Mango Gift Box",
#         "description": "Assorted premium mangoes in an elegant gift box",
#         "price": 49.99,
#         "image_url": "https://farm-fresh-shop-images.s3.amazonaws.com/mango_gift_box.jpg",
#         "type": "Gift Box"
#     },
# ]

# def init_db(db: Session) -> None:
#     # Create admin user
#     user = db.query(User).filter(User.email == "admin@farmfreshshop.com").first()
#     if not user:
#         user = User(
#             email="admin@farmfreshshop.com",
#             username="admin",
#             hashed_password=get_password_hash("admin123"),  # Change in production
#             address="Admin Address",
#             is_admin=True,
#         )
#         db.add(user)
#         logger.info("Created admin user")
    
#     # Create products
#     for product_data in INITIAL_PRODUCTS:
#         product = db.query(Product).filter(Product.name == product_data["name"]).first()
#         if not product:
#             product = Product(**product_data)
#             db.add(product)
#             logger.info(f"Created product: {product_data['name']}")
    
#     db.commit()
#     logger.info("Database initialized")
