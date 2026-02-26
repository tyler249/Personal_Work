import { pipe } from "../utils/pipe.js";
import { verifyUserSession, loadUserDataBundle, sendResponse, handleError } from "../filters";

// Fetch User + Events + Types
export const getUserDataPipeline = pipe(
    verifyUserSession,
    loadUserDataBundle,
    sendResponse(),
    handleError
);
