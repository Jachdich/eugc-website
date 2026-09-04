export async function get_people_names(): Promise<Map<number, string>> {
    let table = await fetch("/api/v1/get_people_names");
    let json = await table.json();
    let result = new Map();
    for (const row of json["rows"]) {
        result.set(row[0], row[1]);
    }
    return result;
}
export const MONDAY   = 0b0000001;
export const TUESDAY  = 0b0000010;
export const WEDNESDAY= 0b0000100;
export const THURSDAY = 0b0001000;
export const FRIDAY   = 0b0010000;
export const SATURDAY = 0b0100000;
export const SUNDAY   = 0b1000000;
    
