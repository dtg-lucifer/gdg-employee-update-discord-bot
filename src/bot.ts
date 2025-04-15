import { Client } from "discord.js";
import { handleMessage } from "./handlers/message-handler";
import { scheduleMorningReminders } from "./schedulers/morning-reminder";
import { scheduleNightlySummary } from "./schedulers/night-summary";
import http from "http";

import dotenv from "dotenv";
import { CONFIG } from "./config/config";

dotenv.config();

// @INFO Start HTTP server for health check route
const server = http.createServer((req, res) => {
  if (req.url === "/health" && req.method === "GET") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(
      JSON.stringify({
        status: "ok",
        uptime: process.uptime(),
        timestamp: new Date().toISOString(),
      })
    );
    return;
  }
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("Discord bot is running!");
});

const PORT = process.env.PORT || 8080;

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

  scheduleMorningReminders(client);
  scheduleNightlySummary(client);

  // @INFO Start HTTP server for health check route
  server.listen(PORT, () => {
    console.log(`HTTP server listening on port ${PORT}`);
  });
});

client.on("messageCreate", handleMessage);

client.login(process.env.BOT_TOKEN);
