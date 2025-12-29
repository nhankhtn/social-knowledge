#!/bin/bash
# Build and push Docker image to Docker Hub

# Configuration
IMAGE_NAME="${DOCKER_USERNAME:-your-username}/social-knowledge-backend"
VERSION="${1:-latest}"

echo "Building Docker image: ${IMAGE_NAME}:${VERSION}"

# Build the image
docker build -t ${IMAGE_NAME}:${VERSION} .

# Tag as latest if not already
if [ "$VERSION" != "latest" ]; then
    docker tag ${IMAGE_NAME}:${VERSION} ${IMAGE_NAME}:latest
fi

echo "Build complete!"
echo ""
echo "To push to Docker Hub, run:"
echo "  docker login"
echo "  docker push ${IMAGE_NAME}:${VERSION}"
if [ "$VERSION" != "latest" ]; then
    echo "  docker push ${IMAGE_NAME}:latest"
fi

