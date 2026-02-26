import { createUser } from "../services/user.service.js";

// Insert new user into database
export async function createUserRecord(req, res, next) {
    try {
        const { userName, email, password } = req.parsed;

        const newUser = await createUser(userName, email, password);

        req.result = { id: newUser.id, userName: newUser.userName, email: newUser.email };
        next();
    } catch (error) {
        next(error);
    }
}
