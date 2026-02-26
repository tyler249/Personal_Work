import { pipe } from "../utils/pipe.js";
import { parseRequest, validateFields, hashPassword, createUserRecord, findUserByName, comparePasswords, sendResponse, handleError } from "../filters";

// User Signup
export const signupPipeline = pipe(
    parseRequest(["userName", "email", "password"]),
    validateFields(["userName", "email", "password"]),
    hashPassword,
    createUserRecord,
    sendResponse({ status: 201, message: "User created successfully" }),
    handleError
);

// User Login
export const loginPipeline = pipe(
    parseRequest(["userName", "password"]),
    validateFields(["userName", "password"]),
    findUserByName,
    comparePasswords,
    sendResponse({ status: 200, message: "Login successful" }),
    handleError
);

// User Logout
export const logoutPipeline = pipe(
    (req, res, next) => {
        req.session.destroy(err => {
            if (err) return next(err);
            res.json({ message: "Logged out successfully" });
        });
    }
);
