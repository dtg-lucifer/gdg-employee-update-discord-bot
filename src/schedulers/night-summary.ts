import cron from "node-cron";
import { CONFIG } from "../config/config";
import { getTodayUpdates, clearTodayUpdates } from "../services/db";
import { buildSummaryEmbed } from "../utils/embed-builder";
import { cleanChannelMessages } from "../utils/cleaner";
import { Client, TextChannel } from "discord.js";

export const scheduleNightlySummary = (client: Client) => {
  cron.schedule(CONFIG.SUMMARY_TIME, async () => {
    try {
      const updates = await getTodayUpdates();
      if (!updates || updates.length === 0) {
        console.log("No updates found for today");
        return;
      }

      const embed = buildSummaryEmbed(updates);

      const summaryChannel = await client.channels.fetch(
        CONFIG.SUMMARY_CHANNEL_ID
      );

      if (summaryChannel && summaryChannel.isTextBased()) {
        await (summaryChannel as TextChannel).send({ embeds: [embed] });
        console.log("Summary sent successfully");
      } else {
        console.error("Summary channel not found or not a text channel");
      }

      await cleanChannelMessages(client, CONFIG.UPDATE_CHANNEL_ID);
      await clearTodayUpdates();
    } catch (error) {
      console.error("Error in night summary scheduler:", error);
    }
  });
};

export const sendNightlySummary = async (client: Client) => {
  try {
    const updates = await getTodayUpdates();
    if (!updates || updates.length === 0) {
      console.log("No updates found for today");
      return;
    }

    const embed = buildSummaryEmbed(updates);

    const summaryChannel = await client.channels.fetch(
      CONFIG.SUMMARY_CHANNEL_ID
    );

    if (summaryChannel && summaryChannel.isTextBased()) {
      await (summaryChannel as TextChannel).send({ embeds: [embed] });
      console.log("Summary sent successfully");
    } else {
      console.error("Summary channel not found or not a text channel");
    }

    await cleanChannelMessages(client, CONFIG.UPDATE_CHANNEL_ID);
    await clearTodayUpdates();
  } catch (error) {
    console.error("Error in night summary scheduler:", error);
  }
};
