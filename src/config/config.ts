import {
  ActivityType,
  GatewayIntentBits,
  Partials,
  type PresenceStatusData,
} from "discord.js";

export const CONFIG = {
  UPDATE_CHANNEL_ID: "1361735268775887039",
  PROD_BOT_ID: "1361701203276206314", // @NOTE Production BOT
  DEV_BOT_ID: "1362446596062576973", // @NOTE Development BOT
  SUMMARY_CHANNEL_ID: "1361735386115866655",
  GUILD_ID: "1293550314552823840",
  MANAGEMENT_ROLE_ID: "1293567884894929049",
  ROLE_ID: ["1293566872465309716", "1293566738847367178"],
  REMINDER_TIME: "0 11 * * *",
  SUMMARY_TIME: "0 23 * * *",
  INTENTS: [
    // Standard intents
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildWebhooks,
    GatewayIntentBits.GuildIntegrations,
    GatewayIntentBits.GuildInvites,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.GuildMessageTyping,
    GatewayIntentBits.GuildScheduledEvents,
    GatewayIntentBits.DirectMessages,

    // Privileged intents - must be enabled in Developer Portal
    GatewayIntentBits.MessageContent, // Requires verification
    GatewayIntentBits.GuildMembers, // Requires verification
    GatewayIntentBits.GuildPresences, // Requires verification
  ],
  PARTIALS: [
    Partials.User,
    Partials.Message,
    Partials.GuildMember,
    Partials.GuildScheduledEvent,
    Partials.Reaction,
    Partials.ThreadMember,
    Partials.Channel,
  ],
  PRESENSE: {
    activities: [
      {
        name: "your minds",
        type: ActivityType.Streaming,
        state: "on fire",
        url: "https://gdgtiu.org",
      },
    ],
    status: "idle" as PresenceStatusData,
  },
};
