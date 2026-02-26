import { getUserEvents } from "../services/event.service.js";

// Load events for a user and date
export async function loadUserEvents(req, res, next) {
    try {
        const { user_id, date } = req.parsed;

        const events = await getUserEvents(user_id, date);

        req.result = { events }; // Attach events to result
        next();
    } catch (error) {
        next(error);
    }
}
