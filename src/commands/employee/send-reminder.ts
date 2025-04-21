import {
  GuildMember,
  MessageFlags,
  SlashCommandBuilder,
  type CommandInteraction,
  type Interaction,
} from "discord.js";
import { sendMorningReminder } from "../../schedulers/morning-reminder";
import { embedBuilder } from "../../utils/embed-builder";
import { CONFIG } from "../../config/config";

const sendReminder_execute = async (interaction: CommandInteraction) => {
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

    const embed = embedBuilder(
      "Success!",
      "Sending morning reminders to all users..."
    );

    // First reply to the interaction within the 3-second window
    if (!interaction.replied && !interaction.deferred) {
      await interaction.reply({
        embeds: [embed],
        flags: MessageFlags.Ephemeral,
      });
    }

    // Then start the potentially longer task of sending reminders
    await sendMorningReminder(interaction.client);
  } catch (error: any) {
    if (error.code === 10062) {
      console.log("Interaction expired before response could be sent");
      return;
    }
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
    if (!interaction.isCommand()) return;
    await sendReminder_execute(interaction as CommandInteraction);
  },
};
