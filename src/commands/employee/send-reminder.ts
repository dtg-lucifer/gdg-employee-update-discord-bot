import {
  GuildMember,
  MessageFlags,
  SlashCommandBuilder,
  type Interaction,
} from "discord.js";
import { sendMorningReminder } from "../../schedulers/morning-reminder";
import { embedBuilder } from "../../utils/embed-builder";
import { CONFIG } from "../../config/config";

const sendReminder_execute = async (interaction: Interaction) => {
  if (!interaction.isCommand()) return;
  if (interaction.commandName !== "send-reminder") return;
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
    const embed = embedBuilder(
      "Success!",
      "Sending morning reminders to all users..."
    );
    sendMorningReminder(interaction.client);
    await interaction.reply({
      embeds: [embed],
      flags: MessageFlags.Ephemeral,
    });
  } catch (error) {
    console.error("Error sending morning reminder:", error);
  }
};

const sendReminder_command = new SlashCommandBuilder()
  .setName("send-reminder")
  .setDescription("Send reminders to all users")
  .toJSON();

export default {
  data: sendReminder_command,
  async execute(interaction: Interaction) {
    await sendReminder_execute(interaction);
  },
};
