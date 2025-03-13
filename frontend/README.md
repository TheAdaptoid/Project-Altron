# Directory Structure

```bash
FRONTEND
 ┣ components # HTML components
 ┃  ┗ conversation_card.html
 ┣ scripts # TypeScript files
 ┃  ┣ conversation_card.ts
 ┃  ┗ requests.ts
 ┣ styles # CSS files
 ┃  ┣ conversation_pane.css
 ┃  ┗ main.css
 ┣ index.html # Root HTML file
 ┗ README.md # Project documentation
```

<br>

# Technology Stack

- **UI Framework**: Vanilla [TypeScript](https://www.typescriptlang.org/)
- **Component Library**: [HTML](https://developer.mozilla.org/en-US/docs/Web/HTML)
- **Styling**:  [CSS](https://developer.mozilla.org/en-US/docs/Web/CSS)

<br>

# Usage Instructions

1. Run the following commands in the terminal:

    ```bash
    cd frontend
    tsc --init
    ```

2. Edit the `tsconfig.json` file to set the `module` option to `ESNext` and the `moduleResolution` option to `classic`.

3. Compile the TypeScript code:

    ```bash
    tsc
    ```

4. Start a local server using Python.
    ```bash
    python3 -m http.server 8001
    ```

5. Go to `http://localhost:8001` in a web browser.

### Supported Browsers

- [x] Chromium (Chrome, Edge)
- [x] Safari
- [ ] Firefox
- [ ] Opera
- [ ] Internet Explorer

<br>

# Design Decisions

## TypeScript vs. JavaScript

I chose to use TypeScript as the primary scripting language becuase I have grown used to type hinting in python and wanted to carry over those same semantics.

## Function over Form

I prioritized full feature functionality over a prettier interface. Going into this project I had a lot of ideas on how things would operate and interact, and to ensure all on those concepts were implemented I focused the bulk of my time on the underlying TypeScript code as opposed to the HTML and CSS styling.

<br>

# Component Reference

## Conversation Card

A component that displays details about a conversation and allows the user to open the conversation in the chat window, rename the conversation, and delete the conversation.

[HTML](components/conversation_card.html) |  [TS](scripts/conversation_card.ts) | CSS

### Attributes

| Attribute          | ID                 | Description                                  |
| ------------------ | ------------------ | -------------------------------------------- |
| title              | conversation-title | The title of the conversation.               |
| last modified date | conversation-time  | The date the conversation was last modified. |
| conversation id    | hidden             | The ID of the conversation.                  |

### Event Listeners

| Action              | Event         | Description                                |
| ------------------- | ------------- | ------------------------------------------ |
| Open conversation   | Element Click | Opens the conversation in the chat window. |
| Rename conversation | Button Press  | Opens a modal to rename the conversation.  |
| Delete conversation | Button Press  | Opens a modal to delete the conversation.  |

<br>

# Development Notes and Future Improvements

- Implement proper [HTML Templating](https://www.w3schools.com/TagS/tag_template.asp).
- Only chromium scroll bars are styled. Need to add support for other browsers.
- Need to add support for dark mode.
