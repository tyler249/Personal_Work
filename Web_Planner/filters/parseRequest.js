// Parse specified fields from req.body or req.query into req.parsed
export function parseRequest(fields, source = "body") {
    return (req, res, next) => {
        req.parsed = {};
        const sourceData = source === "query" ? req.query : req.body;

        fields.forEach(field => {
            req.parsed[field] = sourceData[field];
        });

        next();
    };
}
