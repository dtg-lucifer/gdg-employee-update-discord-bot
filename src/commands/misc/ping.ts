import {
  MessageFlags,
  SlashCommandBuilder,
  type CommandInteraction,
  type Interaction,
} from "discord.js";
import { embedBuilder } from "../../utils/embed-builder";

const ping_execute = async (interaction: CommandInteraction) => {
  try {
    // Mark interaction as handled
    (interaction as any).__handled = true;

    // Check if interaction has already been replied to
    if (interaction.replied || interaction.deferred) {
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
    if (error.code === 10062) {
      console.log("Interaction expired before response could be sent");
      return;
    }
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
    if (!interaction.isCommand()) return;
    await ping_execute(interaction as CommandInteraction);
  },
};
