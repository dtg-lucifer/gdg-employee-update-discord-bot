import { CommandInteraction, MessageFlags, type Interaction } from "discord.js";

export const interactionHandler = async (interaction: Interaction) => {
  if (!interaction.isCommand()) return;

  const { commandName } = interaction;

  // Get the command from the client's commands collection
  const command = (interaction.client as any).commands?.get(commandName);

  if (!command) {
    try {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({
          content: "Command not found",
          flags: MessageFlags.Ephemeral,
        });
      }
    } catch (error: any) {
      console.error(`Command not found error: ${error.message}`);
    }
    return;
  }

  try {
    await command.execute(interaction as CommandInteraction);
  } catch (error: any) {
    console.error("Error executing command:", error);

    // Try to respond with an error message if not already responded
    try {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({
          content: "There was an error while executing this command!",
          flags: MessageFlags.Ephemeral,
        });
      } else if (interaction.replied) {
        await interaction.followUp({
          content: "There was an error while executing this command!",
          flags: MessageFlags.Ephemeral,
        });
      }
    } catch (followUpError) {
      console.error("Could not send error message:", followUpError);
    }
  }
};
