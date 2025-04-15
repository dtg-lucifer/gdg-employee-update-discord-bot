import cron from "node-cron";
import { Client, GuildMember } from "discord.js";
import { CONFIG } from "../config/config";

export const scheduleMorningReminders = (client: Client) => {
  cron.schedule(CONFIG.REMINDER_TIME, async () => {
    const guild = client.guilds.cache.first();

    // Get all roles from the CONFIG.ROLE_ID array
    const roles = CONFIG.ROLE_ID.map((roleId) =>
      guild?.roles.cache.get(roleId)
    ).filter((role) => role !== undefined);

    // Collect unique members from all roles
    const memberSet = new Set<GuildMember>();
    roles.forEach((role) => {
      role?.members.forEach((member) => {
        memberSet.add(member);
      });
    });

    // Send reminders to all members
    memberSet.forEach((member) => {
      member
        .send(
          "👋 Hey! Don't forget to post your update for the day in the updates channel."
        )
        .catch(console.error);
    });
  });
};
