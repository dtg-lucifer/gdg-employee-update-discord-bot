import express from "express";
import { Client } from "discord.js";
import { indexRouter } from "./routes";
import { errorHandler } from "./middlewares/error-handler";
import { CommandService } from "../services/command-service";

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

    // @INFO Initialize server
    this.setupMiddlewares();
    this.setupRoutes();
    this.registerCommands(); // @INFO register commands
  }

  async start() {
    return this.server.listen(this.port, () => {
      console.log(`Server is running on port ${this.port}`);
    });
  }

  async registerCommands() {
    try {
      console.log(`Using application ID: ${process.env.BOT_CLIENT_ID}`);
      const commandData = await CommandService.loadCommands(this.client);
      await CommandService.registerWithDiscordAPI(commandData);
    } catch (error) {
      console.error("Error registering commands:", error);
    }
  }

  setupRoutes() {
    console.log("Setting up routes");
    this.server.use("/", indexRouter);
  }

  setupMiddlewares() {
    this.server.use(express.json());
    this.server.use(express.urlencoded({ extended: true }));
    this.server.use(errorHandler);
  }
}

export { ExServer };
