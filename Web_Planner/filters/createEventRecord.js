import { createEvent } from "../services/event.service.js";

// Insert new event into database
export async function createEventRecord(req, res, next) {
    try {
        const { name, description, date, time, user_id, type_id } = req.parsed;

        const newEvent = await createEvent(name, description, date, time, user_id, type_id);

        req.result = newEvent; 
        next();
    } catch (error) {
        next(error);
    }
}
