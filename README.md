# Sunny Store Shop Bot

A Telegram bot for managing a clothing store inventory.

## Features

- Add new items with photos and variants
- Change existing items
- Delete items
- List all items with pagination
- Search items by name, description, code, or color
- View store statistics

## Project Structure

```
.
├── bot/
│   ├── handlers/         # Command handlers
│   ├── services/         # Database and storage services
│   ├── utils/           # Utility functions and constants
│   └── tests/           # Test files
├── .github/
│   └── workflows/       # CI/CD workflows
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
├── deploy.sh           # Deployment script
└── lambda_function.py  # AWS Lambda handler
```

## Setup

1. Create a `.env` file with the following variables:
```
TELEGRAM_BOT_TOKEN_TEST=your_bot_token
MONGODB_CONN_STRING=mongodb://localhost:27017/
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
S3_BUCKET_NAME=your_bucket_name
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

1. Run locally with Docker:
```bash
docker-compose up --build
```

2. Run tests:
```bash
./run_tests.sh
```

## Deployment

1. Deploy to AWS Lambda:
```bash
./deploy.sh
```

2. Set up webhook:
```bash
curl -F "url=https://your-api-gateway-url/prod" https://api.telegram.org/bot<your-bot-token>/setWebhook
```

## Testing

Run tests with coverage:
```bash
pytest bot/tests/ --cov=bot --cov-report=term-missing -v
```

## Contributing

1. Create a new branch
2. Make your changes
3. Add tests
4. Create a pull request

## License

MIT