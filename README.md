# Farm Fresh Shop API

This is the backend API for the Farm Fresh Shop application, built with FastAPI, SQLAlchemy, and PostgreSQL.

## Features

- User authentication with JWT
- Product management
- Category management
- Order processing
- Admin dashboard

## Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker and Docker Compose (optional)

### Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/farm-fresh-shop.git
cd farm-fresh-shop/farm_fresh_shop_api
```

2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`

```bash
cp .env.example .env
# Edit the .env file with your configuration
```

5. Run the application

```bash
uvicorn main:app --reload
```

### Using Docker

Alternatively, you can use Docker Compose to run the application:

```bash
docker-compose up -d
```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Deployment

This API is designed to be deployed to AWS using various services:

1. **API**: AWS Lambda with API Gateway or ECS with Fargate
2. **Database**: Amazon RDS for PostgreSQL
3. **Storage**: Amazon S3 for product images
4. **Caching**: Amazon ElastiCache (optional)

## AWS Deployment Plan

For deploying this application to AWS, we recommend the following services:

### Recommended AWS Plan

#### For Development/Testing:
- **AWS Lambda** with API Gateway for the FastAPI backend
- **Amazon RDS** (t3.micro) for PostgreSQL database
- **Amazon S3** for storing product images
- **Amazon CloudFront** for content delivery

#### For Production:
- **Amazon ECS** with Fargate for containerized backend
- **Amazon RDS** (t3.small or higher) for PostgreSQL database
- **Amazon S3** for storing product images
- **Amazon CloudFront** for content delivery
- **Amazon ElastiCache** for Redis caching
- **Amazon CloudWatch** for monitoring
- **AWS WAF** for security

### Estimated Costs

#### Development/Testing Plan (Monthly):
- AWS Lambda: ~$5-10/month (depends on traffic)
- Amazon RDS (t3.micro): ~$15-25/month
- Amazon S3: ~$1-5/month
- Amazon CloudFront: ~$1-5/month
- Total: ~$22-45/month

#### Production Plan (Monthly):
- Amazon ECS with Fargate: ~$40-80/month
- Amazon RDS (t3.small): ~$30-50/month
- Amazon S3: ~$5-15/month
- Amazon CloudFront: ~$10-30/month
- Amazon ElastiCache: ~$15-30/month
- Amazon CloudWatch: ~$5-15/month
- AWS WAF: ~$5-10/month
- Total: ~$110-230/month

### Scaling Considerations

This architecture can easily scale as your application grows. You can:

1. Increase the size of your RDS instance
2. Add read replicas for your database
3. Scale your ECS tasks horizontally
4. Implement a CDN for global distribution

## License

This project is licensed under the MIT License - see the LICENSE file for details.
