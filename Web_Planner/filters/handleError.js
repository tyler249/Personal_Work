// Centralized error handler filter
export function handleError(err, req, res, next) {
    console.error("Error in pipeline:", err);

    res.status(500).json({ error: err.message || "Internal Server Error" });
}
