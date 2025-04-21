import { Client, REST, Routes } from "discord.js";
import path from "path";
import { findCommandFiles } from "../utils/file-utils";
import { CONFIG } from "../config/config";

/**
 * Handles loading and registering Discord bot commands
 */
export class CommandService {
  /**
   * Imports and processes a command from a file path
   * @param filePath Path to the command file
   * @param client Discord client to register commands to
   * @returns Command data for Discord API registration, or null if invalid
   */
  static async importCommandFile(
    filePath: string,
    client: Client
  ): Promise<any | null> {
    try {
      const imported = await import(filePath);
      const command = imported.default || imported;

      // Check if command is directly exported or as a property
      if (command && typeof command === "object") {
        // Direct export (default export)
        if ("data" in command && "execute" in command) {
          console.log(`Registering command: ${command.data.name || "unknown"}`);

          // Add to client.commands collection
          if ((client as any).commands) {
            (client as any).commands.set(command.data.name, command);
          }
          return command.data;
        }

        // Check for named exports (find first valid command)
        for (const [key, value] of Object.entries(command)) {
          if (
            value &&
            typeof value === "object" &&
            "data" in value &&
            "execute" in value
          ) {
            console.log(
              `Registering command from named export: ${
                (value.data as any).name || key
              }`
            );

            // Add to client.commands collection
            if ((client as any).commands) {
              (client as any).commands.set((value.data as any).name, value);
            }
            return value.data;
          }
        }
      }

      console.log(`Command at ${filePath} is missing required properties`);
      return null;
    } catch (importError) {
      console.error(`Error importing command file ${filePath}:`, importError);
      return null;
    }
  }

  /**
   * Loads all commands from the commands directory
   * @param client Discord client
   * @returns Array of command data for Discord API registration
   */
  static async loadCommands(client: Client): Promise<any[]> {
    const commandsFolder = path.resolve(process.cwd(), "src/commands");
    const commandFiles = findCommandFiles(commandsFolder);
    console.log(`Found ${commandFiles.length} command files`);

    const commandData: any[] = [];

    for (const filePath of commandFiles) {
      const data = await this.importCommandFile(filePath, client);
      if (data) {
        commandData.push(data);
      }
    }

    return commandData;
  }

  /**
   * Registers commands with Discord API
   * @param client Discord client
   * @param commandData Array of command data for registration
   */
  static async registerWithDiscordAPI(commandData: any[]): Promise<void> {
    if (commandData.length === 0) {
      console.warn("No commands found to register");
      return;
    }

    try {
      const rest = new REST({ version: "10" }).setToken(
        process.env.ENV === "prod"
          ? process.env.PROD_BOT_TOKEN!
          : process.env.DEV_BOT_TOKEN!
      );
      // Use the client ID from environment variables instead of hardcoded CONFIG
      const applicationId =
        process.env.ENV === "prod" ? CONFIG.PROD_BOT_ID : CONFIG.DEV_BOT_ID;

      console.log(`Registering commands for application ID: ${applicationId}`);

      await rest.put(
        Routes.applicationGuildCommands(applicationId, CONFIG.GUILD_ID),
        { body: commandData }
      );
      console.log(`Successfully registered ${commandData.length} commands`);
    } catch (error) {
      console.error("Error registering commands with Discord API:", error);
    }
  }
}
