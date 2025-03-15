import {
  create_conversation,
  retrieve_conversations,
  update_conversation,
  delete_conversation,
  Conversation,
} from "./requests.js";

import { format_date_string } from "./utils.js";

document.addEventListener("DOMContentLoaded", () => {
  // Fetch conversations
  refresh_conversation_list();

  // Link start conversation button
  const start_conversation_button = document.getElementById(
    "start-conversation-button"
  ) as HTMLButtonElement | null;
  start_conversation_button?.addEventListener("click", () => {
    start_new_conversation();
  });
});

async function refresh_conversation_list(): Promise<void> {
  const conversation_list = document.getElementById("conversation-list");

  // If the conversation panel doesn't exist, don't do anything
  if (!conversation_list) return;

  // Remove all existing conversation elements
  conversation_list.innerHTML = "";

  try {
    // Retrieve the first 10 conversations
    const conversations = await retrieve_conversations(0, 50);

    // Create ui elements for each conversation
    conversations.forEach((conversation: Conversation) => {
      fetch("./components/conversation_card.html")
        .then((response) => response.text())
        .then((html) => {
          // Create a new conversation card
          let temp_div = document.createElement("div");
          temp_div.innerHTML = html;
          let conversation_card = temp_div.firstElementChild as HTMLElement;

          // Set the conversation title, time, and id
          (
            conversation_card.querySelector(
              "#conversation-title"
            ) as HTMLElement
          ).textContent = conversation.title;
          (
            conversation_card.querySelector("#conversation-time") as HTMLElement
          ).textContent = format_date_string(
            conversation.updated_at.toString()
          );
          (
            conversation_card.querySelector("#hidden") as HTMLElement
          ).textContent = conversation.id.toString();

          // Set event listener for delete button
          const delete_button = conversation_card.querySelector(
            "#delete-conversation-button"
          );
          delete_button?.addEventListener("click", () => {
            remove_conversation(conversation_card);
          });

          // Set event listener for rename button
          const rename_button = conversation_card.querySelector(
            "#rename-conversation-button"
          );
          rename_button?.addEventListener("click", () => {
            rename_conversation(conversation_card);
          });

          // Append the conversation card to the conversation list
          conversation_list.appendChild(conversation_card);
        });
    });
  } catch (error) {
    console.error(error);
  }
}

export async function start_new_conversation(): Promise<void> {
  // Create API request
  try {
    await create_conversation();
  } catch (error) {
    console.error(error);
  }

  // TODO: Reload Chat Window

  // Reload convo list
  try {
    await refresh_conversation_list();
  } catch (error) {
    console.error(error);
  }
}

async function rename_conversation(
  conversation_card: HTMLElement
): Promise<void> {
  // Get the conversation id
  const conversation_id = parseInt(
    conversation_card.querySelector("#hidden")?.textContent!
  );

  // Open the rename dialog
  const rename_dialog = conversation_card.querySelector(
    "#rename-conversation-dialog"
  ) as HTMLDialogElement;
  rename_dialog.showModal();

  // Wait for the user to submit the form
  rename_dialog.addEventListener("submit", async (event) => {
    event.preventDefault();

    // Get the new title
    const new_title = (
      rename_dialog.querySelector(
        "#rename-conversation-input"
      ) as HTMLInputElement
    ).value;

    // Update the conversation
    try {
      await update_conversation(conversation_id, new_title);
    } catch (error) {
      console.error(error);
    }

    // Reload the conversation list
    try {
      await refresh_conversation_list();
    } catch (error) {
      console.error(error);
    }

    // Close the dialog
    rename_dialog.close();
  });
}

async function remove_conversation(
  conversation_card: HTMLElement
): Promise<void> {
  // Get the conversation id
  const conversation_id = parseInt(
    conversation_card.querySelector("#hidden")?.textContent!
  );

  // Open the delete dialog
  const delete_dialog = conversation_card.querySelector(
    "#delete-conversation-dialog"
  ) as HTMLDialogElement;
  delete_dialog.showModal();

  // Wait for the user to submit the form
  delete_dialog.addEventListener("submit", async (event) => {
    event.preventDefault();

    // Delete API request
    try {
      await delete_conversation(conversation_id);
    } catch (error) {
      console.error(error);
    }

    // TODO: Reload Chat Window

    // Reload convo list
    try {
      await refresh_conversation_list();
    } catch (error) {
      console.error(error);
    }

    // Close the dialog
    delete_dialog.close();
  });
}
