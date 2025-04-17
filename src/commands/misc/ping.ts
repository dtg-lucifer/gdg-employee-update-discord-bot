import {
  MessageFlags,
  SlashCommandBuilder,
  type Interaction,
} from "discord.js";
import { embedBuilder } from "../../utils/embed-builder";

const ping_execute = async (interaction: Interaction) => {
  if (!interaction.isCommand()) return;

  try {
    // @INFO Check if interaction has already been replied to
    if (interaction.replied) {
      console.log("Interaction already replied to, skipping ping response");
      return;
    }

    const embed = embedBuilder("Pong!", "The bot is alive and responding!");

    // Reply with pong
    await interaction.reply({
      embeds: [embed],
      flags: MessageFlags.Ephemeral,
    });
  } catch (error: any) {
    console.error(`Error in ping command: ${error.message}`);
  }
};

const ping_command = new SlashCommandBuilder()
  .setName("ping")
  .setDescription("Ping the bot to check if it's alive")
  .toJSON();

export default {
  data: ping_command,
  async execute(interaction: Interaction) {
    await ping_execute(interaction);
  },
};
