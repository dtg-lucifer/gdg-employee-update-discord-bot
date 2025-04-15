import { Client, TextChannel } from "discord.js";

export const cleanChannelMessages = async (
  client: Client,
  channelId: string
) => {
  try {
    const channel = await client.channels.fetch(channelId);
    if (!channel?.isTextBased()) {
      console.error("Channel is not text-based");
      return;
    }

    const textChannel = channel as TextChannel;
    let messages = await textChannel.messages.fetch({ limit: 100 });

    // Filter messages - keep bot messages, delete others
    const messagesToDelete = messages.filter(
      (message) => !message.author.bot || message.author.id === client.user?.id
    );

    console.log(`Attempting to delete ${messagesToDelete.size} messages`);

    for (const message of messagesToDelete.values()) {
      try {
        await message.delete();
      } catch (err) {
        console.error(`Failed to delete message ${message.id}:`, err);
      }
    }

    console.log("Channel cleanup completed");
  } catch (error) {
    console.error("Error cleaning channel messages:", error);
  }
};
