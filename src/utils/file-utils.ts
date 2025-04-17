import fs from "fs";
import path from "path";

/**
 * Recursively finds all command files in a directory
 * @param directory The directory to search in
 * @returns Array of file paths to command files
 */
export function findCommandFiles(directory: string): string[] {
  const files: string[] = [];

  // Read directory contents
  const items = fs.readdirSync(directory);

  // Process each item (file or directory)
  for (const item of items) {
    const itemPath = path.join(directory, item);
    const stats = fs.statSync(itemPath);

    // If it's a directory, recursively scan it
    if (stats.isDirectory()) {
      const subFiles = findCommandFiles(itemPath);
      files.push(...subFiles);
    }
    // If it's a command file, add it to the result
    else if (item.endsWith(".js") || item.endsWith(".ts")) {
      files.push(itemPath);
    }
  }

  return files;
}
