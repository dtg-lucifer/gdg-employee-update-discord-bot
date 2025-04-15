import {
  ActivityType,
  GatewayIntentBits,
  Partials,
  type PresenceStatusData,
} from "discord.js";

export const CONFIG = {
  UPDATE_CHANNEL_ID: "1361735268775887039",
  SUMMARY_CHANNEL_ID: "1361735386115866655",
  ROLE_ID: ["1293566872465309716", "1293566738847367178"],
  REMINDER_TIME: "0 11 * * *",
  SUMMARY_TIME: "0 23 * * *",
  INTENTS: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
    GatewayIntentBits.GuildMembers,
    GatewayIntentBits.DirectMessages,
    GatewayIntentBits.GuildPresences,
    GatewayIntentBits.GuildMessageTyping,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.GuildScheduledEvents,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildWebhooks,
    GatewayIntentBits.GuildIntegrations,
    GatewayIntentBits.GuildInvites,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.GuildMessageReactions,
    GatewayIntentBits.GuildMessageTyping,
  ],
  PARTIALS: [
    Partials.User,
    Partials.Message,
    Partials.GuildMember,
    Partials.GuildScheduledEvent,
    Partials.Reaction,
    Partials.ThreadMember,
    Partials.GuildScheduledEvent,
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
