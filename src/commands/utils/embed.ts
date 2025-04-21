import {
  MessageFlags,
  Options,
  SlashCommandBuilder,
  SlashCommandChannelOption,
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

const embed_execute = async (interaction: Interaction) => {
  if (!interaction.isCommand()) return;
  if (!interaction.guildId) return;
  if (!interaction.inCachedGuild()) return;
  if (!interaction.guild) return;
  if (!interaction.member) return;

  if (
    !interaction.member.permissions.has("Administrator") &&
    !interaction.member.roles.cache.has(CONFIG.MANAGEMENT_ROLE_ID)
  ) {
    await interaction.reply({
      content: "You do not have permission to use this command.",
      flags: MessageFlags.Ephemeral,
    });
    return;
  }

  const { commandName } = interaction;

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

  if (commandName === "embed") {
    await interaction.reply({
      embeds: [userEmbed],
      flags: MessageFlags.Ephemeral,
    });

    const channel = interaction.options.get("channel")?.channel;
    if (channel && channel.isTextBased()) {
      await channel.send({ embeds: [finalEmbed] });
    }
  }
};

export default {
  data: embed_command,
  async execute(int: Interaction) {
    await embed_execute(int);
  },
};
