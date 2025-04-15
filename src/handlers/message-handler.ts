import { Message } from "discord.js";
import { saveUpdateToDB } from "../services/db";
import { CONFIG } from "../config/config";

export const handleMessage = async (message: Message) => {
  if (message.channelId !== CONFIG.UPDATE_CHANNEL_ID || message.author.bot)
    return;
  try {
    await saveUpdateToDB(
      message.author.id,
      message.author.username,
      message.content
    );
  } catch (error) {
    console.error("Error handling message:", error);
  }
};
