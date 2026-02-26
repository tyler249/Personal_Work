import { pipe } from "../utils/pipe.js";
import { parseRequest, validateFields, createTypeRecord, sendResponse, handleError } from "../filters";

// Create New Type
export const createTypePipeline = pipe(
    parseRequest(["name", "importance", "color"]),
    validateFields(["name", "importance", "color"]),
    createTypeRecord,
    sendResponse({ status: 201, message: "Type created successfully" }),
    handleError
);
