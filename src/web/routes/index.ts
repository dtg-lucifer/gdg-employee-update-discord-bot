import { Router } from "express";
import { healthRouter } from "./health";
import { reminderRouter } from "./reminder";

const indexRouter = Router();

indexRouter.use("/health", healthRouter);
indexRouter.use("/reminder", reminderRouter);

export { indexRouter };
