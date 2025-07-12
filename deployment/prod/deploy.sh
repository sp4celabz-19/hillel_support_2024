# /bin/bash

cd ~/projects/hillel_support_24

git pull
docker compose build && docker compose down && docker compose up -d

echo "Successfully deployed"
