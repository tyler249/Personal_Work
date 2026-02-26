import { createType } from "../services/type.service.js";

// Insert new type into database
export async function createTypeRecord(req, res, next) {
    try {
        const { name, importance, color } = req.parsed;

        const newType = await createType(name, importance, color);

        req.result = newType; 
        next();
    } catch (error) {
        next(error);
    }
}
