import { getUserById, getUserByUserName, createUserInDb } from "../db/queries/user.queries.js";

// Find user by username
export async function findUserByName(userName) {
    return getUserByUserName(userName);
}

// Find user by ID
export async function findUserById(userId) {
    return getUserById(userId);
}

// Create a new user
export async function createUser(userName, email, hashedPassword) {
    return createUserInDb(userName, email, hashedPassword);
}
