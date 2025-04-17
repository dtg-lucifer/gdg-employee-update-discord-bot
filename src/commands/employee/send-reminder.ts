import {
  MessageFlags,
  SlashCommandBuilder,
  type Interaction,
} from "discord.js";
import { sendMorningReminder } from "../../schedulers/morning-reminder";
import { embedBuilder } from "../../utils/embed-builder";

const sendReminder_execute = async (interaction: Interaction) => {
  if (!interaction.isCommand()) return;
  if (interaction.commandName !== "send-reminder") return;
  if (!interaction.guildId) return;

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
