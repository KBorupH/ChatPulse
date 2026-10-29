from errors import MalformedLineError
from models.message import Message, MessageReply
from datetime import datetime, timezone

#EXAMPLE DATA USING FOR PARSING LOGIC FOUND UNDER LOGS IN DATA AND RAW_LINE IN DB UNDER MESSAGES

CHANNEL_COMMANDS = {"PRIVMSG", "USERNOTICE", "CLEARCHAT", "CLEARMSG", "ROOMSTATE", "JOIN", "PART"}
_ESCAPES = {r"\s": " ", r"\:": ";", r"\\": "\\", r"\r": "\r", r"\n": "\n"}

def _unescape(value: str) -> str:
    out, i = [], 0
    while i < len(value):
        pair = value[i:i + 2]
        if pair in _ESCAPES:
            out.append(_ESCAPES[pair])
            i += 2
        else:
            out.append(value[i] if value[i] != "\\" else "")
            i += 1
    return "".join(out)

def _parse_line(raw_line: str) -> dict:
    try:
        tags, prefix, rest = {}, "", raw_line

        if rest.startswith("@"):
            raw_tags, _, rest = rest.partition(" ")
            tags = {key: value for key, _, value in (tag.partition("=") for tag in raw_tags[1:].split(";"))}

        if rest.startswith(":"):
            prefix, _, rest = rest[1:].partition(" ")

        nick, bang, _ = prefix.partition("!")
        user = nick if bang else None

        middle, _, msg_text = rest.partition(" :")
        command, *params = middle.split()

        channel = params[0].removeprefix("#") if command in CHANNEL_COMMANDS and params else None

        return {"tags": tags, "user": user, "command": command,
                "params": params, "channel": channel, "msg": msg_text}
    except (KeyError, ValueError) as e:
        raise MalformedLineError(raw_line, "unsupported format") from e
    
def _parse_ts(tags: dict[str, str]) -> datetime:
    ms = tags.get("tmi-sent-ts")
    if ms is None:
        return datetime.now(timezone.utc)
    return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc) # Twitch sends ts as ms, python works with seconds

def _parse_badges(raw: str) -> dict:
    return {name: version for name, _, version in (b.partition("/") for b in raw.split(",") if b)}

# emotes 
# example: emotes=emotesv2_a3fa2d01a3084aaeb2208a62d0ed9f31:0-18; 
# example: emotes=1035663:0-3
# example: emotes=304985497:11-17,19-25,27-33;
# example: emotes=emotesv2_c2291016906c49179dc6907b5d6d78d0:0-7/emotesv2_2babf27dc9af406f80ea6b0c1268636e:14-27;
# structure: emotes=x:n-m
# x: is id of emote, guarenteed at start
# :n-m is a splice of text, can appear multiple times with if same emote is placed multiple times in same msg
# a / signifies a second or more different emotes
def _parse_emotes(raw: str, text: str) -> tuple[str, ...]:
    names = []
    for emote in filter(None, raw.split("/")):  # filter, equivelant to C# .where, only returns actual values, saves a None check
        _, _, positions = emote.partition(":")
        for pos in positions.split(","):
            start, _, end = pos.partition("-")
            names.append(text[int(start):int(end) + 1])
    return tuple(names)

def _parse_emote_ids(raw: str, text: str) -> dict[str, str]:
    ids = {}
    for emote in filter(None, raw.split("/")): # filter, equivelant to C# .where, only returns actual values, saves a None check
        emote_id, _, positions = emote.partition(":")
        start, _, end = positions.split(",")[0].partition("-")
        ids[text[int(start):int(end)+1]] = emote_id
    return ids

def _parse_reply(tags: dict) -> MessageReply | None:
    if "reply-parent-msg-id" not in tags:
        return None
    parent_name = tags.get("reply-parent-user-login", "")
    
    return MessageReply(
        tags["reply-parent-msg-id"], 
        parent_name,  
        _unescape(tags.get("reply-parent-msg-body", "")))

def _to_message(parsed: dict, raw_line: str) -> Message:
    try:
        tags, text = parsed["tags"], parsed["msg"]
        is_action = text.startswith("\x01ACTION ") and text.endswith("\x01")
        if is_action:
            text = text[8:-1]
        badges = _parse_badges(tags.get("badges", ""))
        return Message(
            raw_line = raw_line,
            platform = "twitch",
            channel = parsed["channel"],
            ts = _parse_ts(tags),
            user = parsed["user"],
            user_id = tags.get("user-id"),
            display_name = _unescape(tags.get("display-name", "")) or parsed["user"],
            text = text,
            color = tags.get("color"),
            msg_id = tags.get("id"),
            emotes = _parse_emotes(tags.get("emotes", ""), text),
            emote_ids = _parse_emote_ids(tags.get("emotes", ""), text),
            bits = int(tags.get("bits", 0)),
            is_broadcaster = "broadcaster" in badges,
            is_mod = tags.get("mod") == "1" or "broadcaster" in badges,
            is_sub = tags.get("subscriber") == "1",
            is_first_msg = tags.get("first-msg") == "1",
            is_action = is_action,
            badges = badges,
            reply = _parse_reply(tags)
        )
    except (KeyError, ValueError) as e:
        raise MalformedLineError(raw_line, "missing or invalid field") from e

def parse(raw_line: str) -> Message | None:
    parsed = _parse_line(raw_line)
    if parsed["command"] != "PRIVMSG":
        return None
    return _to_message(parsed, raw_line)