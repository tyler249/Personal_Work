import { getUserEventsFromDb, createEventInDb } from "../db/queries/event.queries.js";

// Create new event
export async function createEvent(name, description, date, time, userId, typeId) {
    return createEventInDb(name, description, date, time, userId, typeId);
}

// Fetch user events on a specific date
export async function getUserEvents(userId, date) {
    return getUserEventsFromDb(userId, date);
}
