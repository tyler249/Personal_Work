// Send a response based on req.result
export function sendResponse(options = {}) {
    return (req, res, next) => {
        const { status = 200, message = null } = options;

        if (message) {
            return res.status(status).json({ message, data: req.result });
        }

        res.status(status).json(req.result);
    };
}
