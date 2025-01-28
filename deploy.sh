#!/bin/bash

# Create a temporary directory for the package
mkdir -p package

# Install dependencies
pip install -r requirements.txt --target ./package

# Copy our bot code
cp -r bot package/
cp lambda_function.py package/

# Create a ZIP file
cd package
zip -r ../deployment.zip .
cd ..

# Clean up
rm -rf package

# Deploy to AWS Lambda (uncomment and modify as needed)
# aws lambda update-function-code \
#     --function-name your-function-name \
#     --zip-file fileb://deployment.zip

echo "Deployment package created: deployment.zip"