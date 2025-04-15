import { ActivityType, Client, GatewayIntentBits, Partials } from "discord.js";
import { handleMessage } from "./handlers/message-handler";
import { scheduleMorningReminders } from "./schedulers/morning-reminder";
import { scheduleNightlySummary } from "./schedulers/night-summary";
import http from "http";

import dotenv from "dotenv";

dotenv.config();

// Create HTTP server
const server = http.createServer((req, res) => {
  if (req.url === "/health") {
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
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.DirectMessages,
  ],
  allowedMentions: {
    repliedUser: false,
    parse: ["users", "roles"],
  },
  partials: [
    Partials.User,
    Partials.Message,
    Partials.GuildMember,
    Partials.GuildScheduledEvent,
    Partials.Reaction,
    Partials.ThreadMember,
    Partials.GuildScheduledEvent,
    Partials.Channel,
  ],
  presence: {
    activities: [
      {
        name: "your minds",
        type: ActivityType.Streaming,
        state: "on fire",
        url: "https://gdgtiu.org",
      },
    ],
    status: "idle",
  },
});

client.once("ready", () => {
  console.log(`Logged in as ${client.user?.tag}`);
  scheduleMorningReminders(client);
  scheduleNightlySummary(client);

  // Start HTTP server
  server.listen(PORT, () => {
    console.log(`HTTP server listening on port ${PORT}`);
  });
});

client.on("messageCreate", handleMessage);

client.login(process.env.BOT_TOKEN);
