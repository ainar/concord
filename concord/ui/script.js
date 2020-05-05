moment.locale('fr-FR');
marked.setOptions({
    breaks: true,
    gfm: true
})

const messageList = document.getElementById("message-list")
const tabbarList = document.getElementById("tabbar_list");
const sidebarList = document.getElementById("sidebar_list");
let areMessagesAtEnd = true;

function validURL(str) {
    var pattern = /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z0-9\u00a1-\uffff][a-z0-9\u00a1-\uffff_-]{0,62})?[a-z0-9\u00a1-\uffff]\.)+(?:[a-z\u00a1-\uffff]{2,}\.?))(?::\d{2,5})?(?:[/?#]\S*)?$/i
    return !!pattern.test(str);
}

function scrollMessagesToEnd() {
    messageList.scrollTo(0, messageList.scrollHeight);
}

function addMessage(message_id, author, content, time) {
    const messageElement = document.createElement("div");
    const messageMetaElement = document.createElement("div");
    const messageAuthorElement = document.createElement("div");
    const messageTimeElement = document.createElement("div");
    const messageContentElement = document.createElement("div");

    messageElement.setAttribute("id", message_id);
    messageElement.setAttribute("class", "message");
    messageMetaElement.setAttribute("class", "message_meta");
    messageAuthorElement.setAttribute("class", "message_author");
    messageTimeElement.setAttribute("class", "message_time");
    messageContentElement.setAttribute("class", "message_content");

    messageAuthorElement.innerHTML = author;
    messageTimeElement.innerHTML = moment.unix(time).calendar();
    messageContentElement.innerHTML = marked(
        DOMPurify.sanitize(content)
    );

    for (e of messageContentElement.getElementsByTagName('a')) {
        if (validURL(e.innerHTML)) {
            e.style.wordBreak = 'break-all'
        }
        e.setAttribute("target", "_blank")
    }

    messageMetaElement.appendChild(messageAuthorElement);
    messageMetaElement.appendChild(messageTimeElement);
    messageElement.appendChild(messageMetaElement);
    messageElement.appendChild(messageContentElement);

    messageList.appendChild(messageElement);

    if (areMessagesAtEnd) {
        scrollMessagesToEnd();
    }
}

function init() {
    showGuilds();
}

function addGuild(guild_id, guild_name) {
    const listItem = document.createElement("a");
    listItem.setAttribute("class", "tabbar_list_item")
    listItem.setAttribute("href", "#")
    listItem.innerHTML = guild_name
    listItem.addEventListener("click", function () {
        showChannels(guild_id)
    })
    tabbarList.appendChild(listItem)
}

function addChannel(channelId, channelName) {
    const listItem = document.createElement("a");
    listItem.setAttribute("class", "sidebar_list_item")
    listItem.setAttribute("href", "#")
    listItem.innerHTML = channelName
    listItem.addEventListener("click", function () {
        return showMessages(channelId)
    })
    sidebarList.appendChild(listItem)
}

function showChannels(guild_id) {
    sidebarList.textContent = ""
    pywebview.api.get_channels(guild_id)
}

function showGuilds() {
    tabbarList.textContent = ""
    pywebview.api.get_guilds()
}

async function showMessages(channel_id) {
    messageList.textContent = ""
    pywebview.api.get_messages(channel_id)
}

let scrollPercentage = 1;

messageList.addEventListener("scroll", function () {
    areMessagesAtEnd = (messageList.scrollHeight - messageList.clientHeight) <= (messageList.scrollTop + 1);

    if (messageList.scrollHeight > 0) {
        scrollPercentage = messageList.scrollTop * 100 / messageList.scrollHeight;
    }
})

window.addEventListener("resize", function () {
    messageList.scrollTo(0, scrollPercentage * messageList.scrollHeight / 100);

    if (areMessagesAtEnd) {
        scrollMessagesToEnd()
    }
})

let initialized = false;

window.addEventListener('pywebviewready', function () {
    console.log('webview ready')
    if (!initialized) {
        init();
        initialized = true;
    }
})