with open("scripts/deploy.sh", "r") as f:
    content = f.read()

content = content.replace("docker compose up --build -d", "docker builder prune -af\n  docker compose build --no-cache\n  docker compose up -d")

with open("scripts/deploy.sh", "w") as f:
    f.write(content)
