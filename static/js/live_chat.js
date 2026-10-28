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

    const userStatus = ""
    if (msg.is_broadcaster) 
        userStatus = " [Broadcaster]"
    else if (msg.is_mod) 
        userStatus = " [Mod]"

    name.style.color = msg.color || defaultColor(msg.user);

    const text = document.createElement("span");
    text.textContent = msg.is_action ? ` ${msg.text}` : `${userStatus}: ${msg.text}`;
    if (msg.is_action) 
        text.classList.add("fst-italic");

    li.append(`${time} `, name, text);
    return li;
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