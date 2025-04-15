# gdg-updates-discord-bot

To install dependencies:

```bash
bun install
```

To run:

```bash
bun run index.ts
```

## Docker Deployment

You can run this application using Docker:

```bash
docker-compose up -d
```

The application uses PostgreSQL for data storage. A Docker volume (`postgres-data`) ensures data is preserved across container restarts.

This project was created using `bun init` in bun v1.2.7. [Bun](https://bun.sh) is a fast all-in-one JavaScript runtime.
