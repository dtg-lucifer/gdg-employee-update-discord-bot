import { EmbedBuilder } from "discord.js";

export const buildSummaryEmbed = (updates: any[]) => {
  const embed = new EmbedBuilder()
    .setTitle(`📋 Daily Summary - ${new Date().toDateString()}`)
    .setAuthor({
      name: "GDG On Campus TIU",
      url: "https://devx.gdgtiu.org",
    })
    .setFooter({
      text: "Developer: Piush Bose",
      iconURL:
        "https://storage.googleapis.com/leaderboard-pfp/assets/gdg_logo.jpeg",
    })
    .setThumbnail(
      "https://storage.googleapis.com/leaderboard-pfp/assets/gdg_logo.jpeg"
    )
    .setColor(0x00ae86)
    .setTimestamp();

  updates.forEach((update) => {
    embed.addFields({
      name: `**${update.username}**`,
      value: `*${update.content}*`,
    });
  });

  embed.setDescription(
    "Here are the updates for today. Thank you for your contributions!"
  );

  return embed;
};

export const embedBuilder = (title: string, description: string) => {
  const embed = new EmbedBuilder()
    .setTitle(title)
    .setAuthor({
      name: "GDG On Campus TIU",
      url: "https://devx.gdgtiu.org",
    })
    .setDescription(description)
    .setColor(0x00ae86)
    .setTimestamp()
    .setFooter({
      text: "Developer: Piush Bose",
      iconURL:
        "https://storage.googleapis.com/leaderboard-pfp/assets/gdg_logo.jpeg",
    })
    .setThumbnail(
      "https://storage.googleapis.com/leaderboard-pfp/assets/gdg_logo.jpeg"
    );

  return embed;
};
