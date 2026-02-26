export function pipe(...filters) {
    return filters.reduce((a, b) => (req, res, next) => a(req, res, (err) => {
        if (err) return next(err);
        b(req, res, next);
    }));
}
