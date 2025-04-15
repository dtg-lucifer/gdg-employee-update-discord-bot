FROM oven/bun:1-alpine

WORKDIR /app

COPY . .

RUN bun install

VOLUME [ "/app/db" ]

CMD ["bun", "run", "index.ts"]