const text_area = document.getElementById(
  "conversation-input-text"
) as HTMLTextAreaElement;

const input_form = document.getElementById(
  "conversation-input"
) as HTMLFormElement;

// Adjust the height of the textarea
text_area.addEventListener("input", () => {
  text_area.style.height = "auto";
  text_area.style.height = Math.min(text_area.scrollHeight, 150) + "px"; // Needs to be updaed in the CSS too.
});

// Take in user input
input_form.addEventListener("keydown", async (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    await submit_message(input_form);
  }
});
input_form.addEventListener("submit", async (event) => {
  event.preventDefault();
  await submit_message(input_form);
});

async function submit_message(form: HTMLFormElement): Promise<void> {
  const form_data = new FormData(form);

  const user_message: string = form_data.get(
    "conversation-input-text"
  ) as string;

  if (user_message.trim() !== "") {
    await create_message(1, user_message.trim());
    text_area.value = "";
  }
}

async function create_message(
  conversation_id: number,
  text: string
): Promise<void> {
  // Create api request

  // Create ui element

  // Append to convo window

  // Trigger agent response
  console.log(text);
}
