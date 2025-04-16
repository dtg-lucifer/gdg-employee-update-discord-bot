import { Router } from "express";

const reminderRouter = Router();

reminderRouter.get("/", (req, res) => {
  // @TODO get all the remaining updates from the employee_updates table and return as JSON response
  const updates = await get();
  res.status(200).send("OK");
});

export { reminderRouter };
