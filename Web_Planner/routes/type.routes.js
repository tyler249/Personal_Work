import express from "express";
import { createTypePipeline } from "../pipelines/type.pipeline.js";

const router = express.Router();

// Create Type Route
router.post("/", createTypePipeline);

export default router;
