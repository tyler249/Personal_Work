// Verify if user session is valid
export function verifyUserSession(req, res, next) {
    const userId = req.parsed?.user_id || req.headers["user-id"];

    if (!userId) {
        return res.status(401).json({ error: "Unauthorized: No user ID provided" });
    }

    req.userId = userId;
    next();
}
