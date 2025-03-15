/**
 * The type `Conversation` represents a conversation with properties including id, title, created_at,
 * and updated_at.
 * @property {number} id - The `id` property in the `Conversation` type represents a unique identifier
 * for each conversation. It is typically a number used to distinguish one conversation from another.
 * @property {string} title - The `title` property in the `Conversation` type represents the title or
 * name of the conversation. It is a string type field where you can provide a descriptive title for
 * the conversation.
 * @property {Date} created_at - The `created_at` property in the `Conversation` type represents the
 * date and time when the conversation was created. It is of type `Date`, which stores the timestamp of
 * when the conversation was initiated.
 * @property {Date} updated_at - The `updated_at` property in the `Conversation` type represents the
 * date and time when the conversation was last updated. This property is of type `Date`, which stores
 * both the date and time information. It is used to track the most recent update made to the
 * conversation.
 */
export type Conversation = {
  id: number;
  title: string;
  created_at: Date;
  updated_at: Date;
};

/**
 * The function `create_conversation` sends a POST request to create a new conversation and returns the
 * newly created conversation object.
 *
 * @returns The `create_conversation` function returns a Promise that resolves to a `Conversation`
 * object.
 * @throws Will throw an error if the conversation creation fails.
 */
export async function create_conversation(): Promise<Conversation> {
  const response = await fetch("http://localhost:8000/conversations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    throw new Error("Failed to create conversation");
  }

  const conversation: Conversation = await response.json();
  return conversation;
}

/**
 * The function `retrieve_conversations` sends a GET request to retrieve a list of conversations,
 * filtering out the first `skip` number of conversations and returning the next `limit` number of
 * conversations.
 *
 * @param {number} skip - The number of conversations to skip before retrieving the list of
 * conversations.
 * @param {number} limit - The number of conversations to return.
 * @returns The `retrieve_conversations` function returns a Promise that resolves to an array of
 * `Conversation` objects.
 * @throws Will throw an error if the retrieval fails.
 */
export async function retrieve_conversations(
  skip: number,
  limit: number
): Promise<Conversation[]> {
  const response = await fetch(
    `http://localhost:8000/conversations/?skip=${skip}&limit=${limit}`
  );

  if (!response.ok) {
    throw new Error("Failed to retrieve conversations");
  }

  const conversations: Conversation[] = await response.json();
  return conversations;
}

/**
 * The function `update_conversation` sends a PATCH request to update the title of an existing conversation
 * with the specified ID and returns the updated conversation object.
 *
 * @param {number} id - The ID of the conversation to update.
 * @param {string} title - The new title to update the conversation with.
 * @returns {Promise<Conversation>} A Promise that resolves to the updated `Conversation` object.
 * @throws Will throw an error if the update fails.
 */
export async function update_conversation(
  id: number,
  title: string
): Promise<Conversation> {
  const response = await fetch(`http://localhost:8000/conversations/${id}`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ title }),
  });

  if (!response.ok) {
    throw new Error("Failed to update conversation");
  }

  const conversation: Conversation = await response.json();
  return conversation;
}

/**
 * Sends a DELETE request to remove a conversation with the specified ID.
 *
 * @param {number} id - The ID of the conversation to delete.
 * @returns {Promise<void>} A Promise that resolves when the deletion is complete.
 * @throws Will throw an error if the deletion fails.
 */
export async function delete_conversation(id: number): Promise<void> {
  const response = await fetch(`http://localhost:8000/conversations/${id}`, {
    method: "DELETE",
  });

  if (!response.ok) {
    throw new Error("Failed to delete conversation");
  }
}
