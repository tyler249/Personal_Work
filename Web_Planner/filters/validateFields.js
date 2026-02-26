// Validate that required fields are present and not empty
export function validateFields(requiredFields) {
    return (req, res, next) => {
        for (const field of requiredFields) {
            if (!req.parsed[field]) {
                return res.status(400).json({ error: `Missing field: ${field}` });
            }
        }
        next();
    };
}
