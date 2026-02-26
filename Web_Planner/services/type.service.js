import { getTypesFromDb, createTypeInDb } from "../db/queries/type.queries.js";

// Create a new type
export async function createType(name, importance, color) {
    return createTypeInDb(name, importance, color);
}

// Get all types
export async function getTypes() {
    return getTypesFromDb();
}
