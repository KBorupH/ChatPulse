const TWITCH_EMOTE_URL = "https://static-cdn.jtvnw.net/emoticons/v2/{id}/default/dark/1.0"; //Obviously needs differing logic with proper multi platform support

const MAX_MESSAGES = 300;
const socket = io();
const lists = {};

document.querySelectorAll(".chat-pane").forEach((pane) => {
    lists[pane.dataset.channelId] = pane.querySelector(".messages");
});

socket.on("connect", () => {
    for (const channelId of Object.keys(lists)) {
        socket.emit("join", { channel_id: Number(channelId) });
    }
});

socket.on("messages", ({ channel_id, messages }) => {
    const list = lists[channel_id];
    if (!list) return;


    const atBottom = list.scrollHeight - list.scrollTop - list.clientHeight < 40;

    for (const msg of messages) {
        list.append(renderMessage(msg));
    }
    while (list.children.length > MAX_MESSAGES) {
        list.firstElementChild.remove();
    }
    if (atBottom) {
        list.scrollTop = list.scrollHeight;
    }
});

function renderMessage(msg) {
    const li = document.createElement("li");
    li.className = "py-1";

    if (msg.reply_to_login) {
        const reply = document.createElement("div");
        reply.className = "small text-body-secondary";
        reply.textContent = `-> @${msg.reply_to_login}: ${msg.reply_to_body}`;
        li.append(reply);
    }

    const time = new Date(msg.sent_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    const name = document.createElement("strong");
    name.textContent = msg.display_name;

    const userStatus = document.createElement("strong");
    if (msg.is_action)
        userStatus.textContent = " "
    else if (msg.is_broadcaster) 
        userStatus.textContent = " [Broadcaster]"
    else if (msg.is_mod) 
        userStatus.textContent = " [Mod]"

    name.style.color = msg.color || defaultColor(msg.user_login);

    const collonSep =  msg.is_action ? " " : ": ";

    const text = renderText(msg.text, msg.emote_ids)
    if (msg.is_action) 
        text.classList.add("fst-italic");

    li.append(`${time} `, name, userStatus, collonSep, text);
    return li;
}

function renderText(text, emoteIds) {
    const span = document.createElement("span");

    text.split(" ").forEach((word, i) => {
        if (i > 0)
            span.append(" ")

        const id = emoteIds[word];
        if (!id){
            span.append(word);
            return;
        }

        const img = document.createElement("img");
        img.src = TWITCH_EMOTE_URL.replace("{id}", encodeURIComponent(id));
        img.className = "emote"
        span.append(img);
    });

    return span;
}

const DEFAULT_COLORS = [
  "#9ACD32",
  "#FF4500",
  "#2E8B57",
  "#DAA520",
  "#D2691E",
  "#5F9EA0",
];

// Use same logic as Twitch, if user has no defined color, pick from array based on their id, making persistent colors for same user.
function defaultColor(login) {
    let sum = 0;

    for (const ch of login) 
        sum += ch.charCodeAt(0);

    return DEFAULT_COLORS[sum % DEFAULT_COLORS.length]; 
}