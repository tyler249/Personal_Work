import express from "express";
import { getUserDataPipeline } from "../pipelines/data.pipeline.js";

const router = express.Router();

// Get all user-related data
router.get("/", getUserDataPipeline);

export default router;
