import { Pool } from "pg";
import { v7 as uuidV7 } from "uuid";
import dotenv from "dotenv";

dotenv.config();

// Initialize PostgreSQL connection pool
const pool = new Pool({
  user: process.env.POSTGRES_USER,
  host: process.env.POSTGRES_HOST,
  database: process.env.POSTGRES_DB,
  password: process.env.POSTGRES_PASSWORD,
  port: parseInt(process.env.POSTGRES_PORT || "5432"),
});

// Initialize the database
const initializeDatabase = async () => {
  try {
    await pool.query(`
      CREATE TABLE IF NOT EXISTS employee_updates (
        id TEXT PRIMARY KEY NOT NULL,
        userId TEXT,
        username TEXT,
        content TEXT,
        date TEXT
      )
    `);
    console.log("Database initialized successfully");
  } catch (error) {
    console.error("Error initializing database:", error);
  }
};

// Call initialization function
initializeDatabase();

export const saveUpdateToDB = async (
  userId: string,
  username: string,
  content: string
) => {
  const date = new Date().toISOString().split("T")[0];
  const id = uuidV7().toString();

  try {
    await pool.query(
      "INSERT INTO employee_updates (id, userId, username, content, date) VALUES ($1, $2, $3, $4, $5)",
      [id, userId, username, content, date]
    );
  } catch (error) {
    console.error("Error saving update to database:", error);
  }
};

export const getTodayUpdates = async () => {
  const date = new Date().toISOString().split("T")[0];

  try {
    const result = await pool.query(
      "SELECT * FROM employee_updates WHERE date = $1",
      [date]
    );
    return result.rows;
  } catch (error) {
    console.error("Error getting today updates:", error);
    return [];
  }
};

export const clearTodayUpdates = async () => {
  const date = new Date().toISOString().split("T")[0];

  try {
    await pool.query("DELETE FROM employee_updates WHERE date = $1", [date]);
  } catch (error) {
    console.error("Error clearing today updates:", error);
  }
};
