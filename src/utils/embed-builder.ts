import { EmbedBuilder } from "discord.js";

export const buildSummaryEmbed = (updates: any[]) => {
  const embed = new EmbedBuilder()
    .setTitle(`📋 Daily Summary - ${new Date().toLocaleDateString()}`)
    .setColor(0x00ae86)
    .setTimestamp();

  updates.forEach((update) => {
    embed.addFields({ name: update.username, value: update.content });
  });

  return embed;
};
