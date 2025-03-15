/**
 * Formats a date string in ISO 8601 format to a more readable format.
 *
 * @param {string} date_string - A date string in ISO 8601 format (e.g., "YYYY-MM-DDTHH:MM:SS.fffZ").
 * @returns {string} The formatted date string in the format "YYYY-MM-DD | HH:MM:SS".
 */
export function format_date_string(date_string: string): string {
  let date: string = date_string.split("T")[0];
  let time: string = date_string.split("T")[1];

  time = time.split(".")[0];

  return `${date} |  ${time}`;
}
