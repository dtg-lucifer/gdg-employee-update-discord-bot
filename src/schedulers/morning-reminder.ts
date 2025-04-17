import cron from "node-cron";
import { Client, GuildMember } from "discord.js";
import { CONFIG } from "../config/config";
import { embedBuilder } from "../utils/embed-builder";

export const scheduleMorningReminders = (client: Client) => {
  cron.schedule(CONFIG.REMINDER_TIME, async () => {
    try {
      await sendMorningReminder(client);
    } catch (error) {
      console.error("Error in scheduled morning reminders:", error);
    }
  });
};

export const sendMorningReminder = async (client: Client) => {
  try {
    // Check if client is ready
    if (!client.isReady()) {
      console.error("Client is not ready for sending reminders");
      return;
    }

    // Get first guild or fetch all guilds if none in cache
    let guild = client.guilds.cache.get(CONFIG.GUILD_ID);
    if (!guild) {
      console.log("No guild in cache, fetching guilds...");
      await client.guilds.fetch();
      guild = client.guilds.cache.first();

      if (!guild) {
        console.error("No guilds found for this bot!");
        return;
      }
    }

    console.log(`Working with guild: ${guild.name} (${guild.id})`);

    // Check if roles exist
    const roleIds = CONFIG.ROLE_ID;
    console.log(`Looking for roles: ${roleIds.join(", ")}`);

    // Make sure members are fetched
    console.log("Fetching guild members...");
    await guild.members.fetch();

    // Get all roles from the CONFIG.ROLE_ID array
    const roles = roleIds
      .map((roleId) => guild?.roles.cache.get(roleId))
      .filter((role) => role !== undefined);

    if (roles.length === 0) {
      console.error("No matching roles found! Check your role IDs.");
      return;
    }

    // Collect unique members from all roles
    const memberSet = new Set<GuildMember>();
    roles.forEach((role) => {
      console.log(`Role ${role?.name}: ${role?.members.size} members`);
      role?.members.forEach((member) => {
        memberSet.add(member);
      });
    });

    console.log(`Found ${memberSet.size} unique members to DM`);

    // If no members found, log an error
    if (memberSet.size === 0) {
      console.error("No members found in the specified roles!");
      return;
    }

    // Send reminders to all members
    let successCount = 0;
    let failCount = 0;

    for (const member of memberSet) {
      try {
        // Skip bots
        if (member.user.bot) continue;

        console.log(`Attempting to DM ${member.user.username}...`);

        const embed = embedBuilder(
          "Morning Reminder",
          "👋 Hey! Don't forget to post your update for the day in the updates channel."
        );
        await member.send({
          embeds: [embed],
          allowedMentions: { users: [member.id] },
        });

        successCount++;
      } catch (error: any) {
        failCount++;
        if (error.code === 50007) {
          console.log(`Cannot DM ${member.user.username}: DMs are disabled`);
        } else {
          console.error(`Failed to DM ${member.user.username}:`, error);
        }
      }
    }

    console.log(`DM Summary: ${successCount} successful, ${failCount} failed`);
  } catch (error) {
    console.error("Error in sendMorningReminder:", error);
    throw error;
  }
};
