import {
  MessageFlags,
  SlashCommandBuilder,
  type CommandInteraction,
  type Interaction,
} from "discord.js";
import { embedBuilder } from "../../utils/embed-builder";

const uptime_command = new SlashCommandBuilder()
  .setName("uptime")
  .setDescription("Get the bot's uptime")
  .toJSON();

// Modified to accept CommandInteraction directly since we know it's a command
async function execute(interaction: CommandInteraction) {
  const uptime = process.uptime();
  const days = Math.floor(uptime / (24 * 60 * 60));
  const hours = Math.floor((uptime % (24 * 60 * 60)) / (60 * 60));
  const minutes = Math.floor((uptime % (60 * 60)) / 60);
  const seconds = Math.floor(uptime % 60);
  const uptimeString = `${days}d ${hours}h ${minutes}m ${seconds}s`;

  try {
    const embed = embedBuilder("Uptime", `Uptime: ${uptimeString}`);
    await interaction.reply({
      embeds: [embed],
      flags: MessageFlags.Ephemeral,
    });
  } catch (error) {
    console.error("Error replying to uptime command:", error);
  }
}

export default {
  data: uptime_command,
  execute,
};
