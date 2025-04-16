import { Router } from "express";

const healthRouter = Router();

healthRouter.get("/", (req, res) => {
  res.status(200).send("OK");
});

healthRouter.get("/health", (req, res) => {
  res.status(200).send({
    status: "ok",
    uptime: process.uptime(),
    timestamp: new Date().toISOString(),
  });
});

healthRouter.get("/ping", (req, res) => {
  res.status(200).send("Pong");
});

export { healthRouter };
