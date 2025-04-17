import {
  GuildMember,
  MessageFlags,
  SlashCommandBuilder,
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

const sendSummary_execute = async (interaction: Interaction) => {
  if (!interaction.isCommand()) return;
  if (interaction.commandName !== "send-summary") return;
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
    await interaction.reply({
      embeds: [embed],
      flags: MessageFlags.Ephemeral,
    });
    return;
  }

  try {
    const ch = interaction.options.get("channel");
    const channel = interaction.guild?.channels.cache.get(ch?.value as string);
    if (!channel) {
      await interaction.reply({
        content: "Please provide a valid text channel.",
        flags: MessageFlags.Ephemeral,
      });
      return;
    }

    if (!channel.isTextBased()) {
      await interaction.reply({
        content: "Please provide a valid text channel.",
        flags: MessageFlags.Ephemeral,
      });
      return;
    }

    await sendNightlySummary(interaction.client);

    const embed = embedBuilder("Success!", `Summary sent to ${channel}`);

    await interaction.reply({
      embeds: [embed],
      flags: MessageFlags.Ephemeral,
    });
  } catch (error) {
    console.error("Error sending summary:", error);
    await interaction.reply({
      content: "There was an error while sending the summary!",
      flags: MessageFlags.Ephemeral,
    });
  }
};

export default {
  data: sendSummary_command,
  async execute(interaction: Interaction) {
    await sendSummary_execute(interaction);
  },
};
