#!/bin/bash
set -e

APP_NAME="alivv-app"
IMAGE="joeljoby3000/alivv-app:latest"

echo "=== Starting Deployment on $(hostname) ==="

# 1. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
else
    echo "Docker is already installed."
fi

# 2. Pull latest image
echo "Pulling latest image: $IMAGE"
sudo docker pull $IMAGE

# 3. Stop and remove existing container
if [ "$(sudo docker ps -aq -f name=$APP_NAME)" ]; then
    echo "Stopping and removing existing container..."
    sudo docker stop $APP_NAME
    sudo docker rm $APP_NAME
fi

# 4. Run new container
# Mapping port 80 (HTTP) to 8000 (app)
# Setting restart policy to always
echo "Starting new container..."
sudo docker run -d \
    --name $APP_NAME \
    --restart always \
    -p 80:8000 \
    -e DEBUG=True \
    -e SECRET_KEY='django-insecure-&kld(=^yx_yqdo8anf^wbk8vfj8arol!v%fm^blruir)aqbri9' \
    -e ALLOWED_HOSTS='*' \
    $IMAGE

echo "=== Deployment Success! ==="
echo "You can view the site at: http://$(curl -s ifconfig.me)"
