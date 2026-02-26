import { pipe } from "../utils/pipe.js";
import { parseRequest, validateFields, verifyUserSession, createEventRecord, loadUserEvents, sendResponse, handleError } from "../filters";

// Create Event
export const createEventPipeline = pipe(
    parseRequest(["name", "date", "type_id", "user_id"]),
    validateFields(["name", "date", "type_id", "user_id"]),
    verifyUserSession,
    createEventRecord,
    sendResponse({ status: 201, message: "Event created successfully" }),
    handleError
);

// Get User Events by Date
export const getUserEventsPipeline = pipe(
    parseRequest(["user_id", "date"], "query"), // read from query params
    validateFields(["user_id", "date"]),
    loadUserEvents,
    sendResponse(),
    handleError
);
