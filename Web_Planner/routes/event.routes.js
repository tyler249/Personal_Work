import express from "express";
import { createEventPipeline, getUserEventsPipeline } from "../pipelines/event.pipeline.js";

const router = express.Router();

// Create Event Route
router.post("/", createEventPipeline);

// Get User Events by Date Route
router.get("/user", getUserEventsPipeline);

export default router;
