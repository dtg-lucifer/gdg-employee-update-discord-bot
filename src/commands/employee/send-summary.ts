import {
  GuildMember,
  MessageFlags,
  SlashCommandBuilder,
  type CommandInteraction,
  type Interaction,
} from "discord.js";
import { sendNightlySummary } from "../../schedulers/night-summary";
import { embedBuilder } from "../../utils/embed-builder";
import { CONFIG } from "../../config/config";

const sendSummary_command = new SlashCommandBuilder()
  .setName("send-summary")
  .setDescription("Send a summary of the last week to all users")
  .addChannelOption((option) =>
    option
      .setName("channel")
      .setDescription("The channel to send the summary to")
      .setRequired(true)
  )
  .toJSON();

const sendSummary_execute = async (interaction: CommandInteraction) => {
  try {
    // Mark interaction as handled
    (interaction as any).__handled = true;

    if (!interaction.guildId) return;

    const member = interaction.member as GuildMember;

    if (
      !member.roles.cache.has(CONFIG.MANAGEMENT_ROLE_ID) &&
      !member.permissions.has("Administrator")
    ) {
      const embed = embedBuilder(
        "Error!",
        "You do not have permission to use this command."
      );

      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({
          embeds: [embed],
          flags: MessageFlags.Ephemeral,
        });
      }
      return;
    }

    const ch = interaction.options.get("channel");
    const channel = interaction.guild?.channels.cache.get(ch?.value as string);
    if (!channel) {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({
          content: "Please provide a valid text channel.",
          flags: MessageFlags.Ephemeral,
        });
      }
      return;
    }

    if (!channel.isTextBased()) {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({
          content: "Please provide a valid text channel.",
          flags: MessageFlags.Ephemeral,
        });
      }
      return;
    }

    // First reply to the interaction within the 3-second window
    const embed = embedBuilder("Success!", `Sending summary to ${channel}`);

    if (!interaction.replied && !interaction.deferred) {
      await interaction.reply({
        embeds: [embed],
        flags: MessageFlags.Ephemeral,
      });
    }

    // Then start the potentially longer task of sending the summary
    await sendNightlySummary(interaction.client);
  } catch (error: any) {
    if (error.code === 10062) {
      console.log("Interaction expired before response could be sent");
      return;
    }
    console.error("Error sending summary:", error);

    try {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({
          content: "There was an error while sending the summary!",
          flags: MessageFlags.Ephemeral,
        });
      }
    } catch (replyError) {
      console.error("Could not send error message:", replyError);
    }
  }
};

export default {
  data: sendSummary_command,
  async execute(interaction: Interaction) {
    if (!interaction.isCommand()) return;
    await sendSummary_execute(interaction as CommandInteraction);
  },
};
