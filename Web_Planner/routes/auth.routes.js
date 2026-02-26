import express from "express";
import { signupPipeline, loginPipeline, logoutPipeline } from "../pipelines/auth.pipeline.js";

const router = express.Router();

// Signup Route
router.post("/signup", signupPipeline);

// Login Route
router.post("/login", loginPipeline);

// Logout Route
router.post("/logout", logoutPipeline);

export default router;
