import {
  MessageFlags,
  SlashCommandBuilder,
  SlashCommandChannelOption,
  type CommandInteraction,
  type Interaction,
} from "discord.js";
import { CONFIG } from "../../config/config";
import { embedBuilder } from "../../utils/embed-builder";

const embed_command = new SlashCommandBuilder()
  .setName("embed")
  .setDescription("Create an embed message")
  .addChannelOption((opt: SlashCommandChannelOption) =>
    opt.setName("channel").setDescription("Select a channel").setRequired(true)
  )
  .addStringOption((opt) =>
    opt
      .setName("title")
      .setDescription("The title of the embed")
      .setRequired(true)
  )
  .addStringOption((opt) =>
    opt
      .setName("description")
      .setDescription("The description of the embed")
      .setRequired(true)
  )
  .toJSON();

const embed_execute = async (interaction: CommandInteraction) => {
  try {
    // Mark interaction as handled
    (interaction as any).__handled = true;

    if (!interaction.guildId) return;
    if (!interaction.inCachedGuild()) return;
    if (!interaction.guild) return;
    if (!interaction.member) return;

    if (
      !interaction.member.permissions.has("Administrator") &&
      !interaction.member.roles.cache.has(CONFIG.MANAGEMENT_ROLE_ID)
    ) {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({
          content: "You do not have permission to use this command.",
          flags: MessageFlags.Ephemeral,
        });
      }
      return;
    }

    const userEmbed = embedBuilder(
      "Success!",
      `
      Embed has been sent successfully to <#${
        interaction.options.get("channel")?.channel?.id
      }>.
      `
    );

    const finalEmbed = embedBuilder(
      interaction.options.get("title")?.value as string,
      interaction.options.get("description")?.value as string,
      "",
      "Piush Bose"
    );

    // First reply to the interaction
    if (!interaction.replied && !interaction.deferred) {
      await interaction.reply({
        embeds: [userEmbed],
        flags: MessageFlags.Ephemeral,
      });
    }

    // Then send to the target channel
    const channel = interaction.options.get("channel")?.channel;
    if (channel && channel.isTextBased()) {
      await channel.send({ embeds: [finalEmbed] });
    }
  } catch (error: any) {
    if (error.code === 10062) {
      console.log("Interaction expired before response could be sent");
      return;
    }
    console.error("Error executing embed command:", error);

    try {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({
          content: "There was an error creating the embed!",
          flags: MessageFlags.Ephemeral,
        });
      }
    } catch (replyError) {
      console.error("Could not send error message:", replyError);
    }
  }
};

export default {
  data: embed_command,
  async execute(int: Interaction) {
    if (!int.isCommand()) return;
    await embed_execute(int as CommandInteraction);
  },
};
