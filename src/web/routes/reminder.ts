import { Router } from "express";
import { sendMorningReminder } from "../../schedulers/morning-reminder";
import { sendNightlySummary } from "../../schedulers/night-summary";
import { getTodayUpdates } from "../../services/db";

const reminderRouter = Router();

reminderRouter.get("/", async (req, res) => {
  try {
    const updates = await getTodayUpdates();
    res.status(200).json(updates);
  } catch (error) {
    console.error("Error fetching updates:", error);
    res.status(500).json({ error: "Failed to fetch updates" });
  }
});

reminderRouter.post("/send-morning", async (req, res) => {
  try {
    const client = (req as any).discordClient;
    if (!client) {
      res.status(500).json({ error: "Discord client not available" });
      return;
    }

    await sendMorningReminder(client);
    res
      .status(200)
      .json({ status: "success", message: "Morning reminders sent" });
  } catch (error) {
    console.error("Error sending morning reminder:", error);
    res.status(500).json({ error: "Failed to send reminders" });
  }
});

reminderRouter.post("/send-summary", async (req, res) => {
  try {
    const client = (req as any).discordClient;
    if (!client) {
      res.status(500).json({ error: "Discord client not available" });
      return;
    }

    await sendNightlySummary(client);
    res.status(200).json({ status: "success", message: "Summary sent" });
  } catch (error) {
    console.error("Error sending nightly summary:", error);
    res.status(500).json({ error: "Failed to send summary" });
  }
});

export { reminderRouter };
