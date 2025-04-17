import { Client, Collection } from "discord.js";
import { handleMessage } from "./handlers/message-handler";
import { ExServer } from "./web/index";

import dotenv from "dotenv";
import { CONFIG } from "./config/config";
import { interactionHandler } from "./handlers/interaction-handler";

dotenv.config();

const PORT = parseInt(process.env.PORT || "8080");

const client = new Client({
  intents: [...CONFIG.INTENTS],
  partials: [...CONFIG.PARTIALS],
  presence: {
    activities: CONFIG.PRESENSE.activities,
    status: CONFIG.PRESENSE.status,
  },
  allowedMentions: {
    repliedUser: false,
    parse: ["users", "roles"],
  },
});

// @INFO Set client as a property on request object
(client as any).commands = new Collection();

client.once("ready", () => {
  console.log(`Logged in as ${client.user?.tag}`);

  const server = new ExServer(PORT, client);
  server.start();
});

client.on("messageCreate", handleMessage);
client.on("interactionCreate", interactionHandler);

client.login(process.env.BOT_TOKEN);
