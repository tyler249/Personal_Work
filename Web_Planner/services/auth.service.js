import bcrypt from "bcryptjs";
import { findUserByName } from "./user.service.js";

// Authenticate user credentials
export async function authenticateUser(userName, password) {
    const user = await findUserByName(userName);

    if (!user) {
        return null;
    }

    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
        return null;
    }

    return user;
}
