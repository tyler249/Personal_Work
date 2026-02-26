import bcrypt from "bcryptjs";
import { getUserByUserName } from "../services/user.service.js";

// Find user and compare passwords
export async function comparePasswords(req, res, next) {
    try {
        const plainPassword = req.parsed.password;
        const user = req.user; 
        
        if (!user) {
            return res.status(401).json({ error: "Invalid username or password" });
        }

        const match = await bcrypt.compare(plainPassword, user.password);

        if (!match) {
            return res.status(401).json({ error: "Invalid username or password" });
        }

        // Password matched
        req.user = { id: user.id, userName: user.userName };
        next();
    } catch (error) {
        next(error);
    }
}
