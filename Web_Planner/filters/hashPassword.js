import bcrypt from "bcryptjs";

// Hash the password inside req.parsed
export async function hashPassword(req, res, next) {
    try {
        const plainPassword = req.parsed.password;
        const hashed = await bcrypt.hash(plainPassword, 10);

        req.parsed.password = hashed;
        next();
    } catch (error) {
        next(error);
    }
}
