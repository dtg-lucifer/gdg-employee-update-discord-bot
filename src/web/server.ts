import express from "express";
import { Client } from "discord.js";
import { indexRouter } from "./routes";
import { errorHandler } from "./middlewares/error-handler";

class ExServer {
  server: express.Express;
  port: number;
  client: Client;

  constructor(port: number, client: Client) {
    this.server = express();
    this.port = port;
    this.client = client;

    // Set client as a property on request object
    this.server.use((req, res, next) => {
      (req as any).discordClient = client;
      next();
    });

    // Initialize server
    this.setupMiddlewares();
    this.setupRoutes();
  }

  start() {
    return this.server.listen(this.port, () => {
      console.log(`Server is running on port ${this.port}`);
    });
  }

  setupRoutes() {
    this.server.use("/", indexRouter);
  }

  setupMiddlewares() {
    this.server.use(express.json());
    this.server.use(express.urlencoded({ extended: true }));
    this.server.use(errorHandler);
  }
}

export { ExServer };
