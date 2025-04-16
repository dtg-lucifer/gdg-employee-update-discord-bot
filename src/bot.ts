import { Client } from "discord.js";
import { handleMessage } from "./handlers/message-handler";
import { ExServer } from "./web/index";

import dotenv from "dotenv";
import { CONFIG } from "./config/config";

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

client.once("ready", () => {
  console.log(`Logged in as ${client.user?.tag}`);

  // Uncomment these if you want to use the scheduled reminders
  // scheduleMorningReminders(client);
  // scheduleNightlySummary(client);

  // Initialize and start the Express server
  const server = new ExServer(PORT, client);
  server.start();
});

client.on("messageCreate", handleMessage);

client.login(process.env.BOT_TOKEN);
