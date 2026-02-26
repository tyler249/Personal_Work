import { getTypes } from "../services/type.service.js";

// Load all available types
export async function loadTypes(req, res, next) {
    try {
        const types = await getTypes();

        req.result = { types }; // Attach types to result
        next();
    } catch (error) {
        next(error);
    }
}
