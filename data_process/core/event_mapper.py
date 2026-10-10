
BOOT_EVENTS = {
    "EVENT_BOOT",
}
# ===============================
# File Operations
# ===============================

READ_EVENTS = {
    "EVENT_READ",
}

WRITE_EVENTS = {
    "EVENT_WRITE",
}

OPEN_EVENTS = {
    "EVENT_OPEN",
}

CLOSE_EVENTS = {
    "EVENT_CLOSE",
}

MODIFY_EVENTS = {
    "EVENT_UNLINK",
    "EVENT_REMOVE",
    "EVENT_RENAME",
    "EVENT_LINK",
    "EVENT_CHMOD",
    "EVENT_CHOWN",
    "EVENT_TRUNCATE",
    "EVENT_MODIFY_FILE_ATTRIBUTES",

}



# ===============================
# Process Operations
# ===============================

EXECUTE_EVENTS = {
    "EVENT_EXECUTE",
    "EVENT_EXECUTE2",
}

CREATE_EVENTS = {
    "EVENT_FORK",
    "EVENT_CLONE",
}

PROCESS_EXIT_EVENTS = {
    "EVENT_EXIT",
}

# ===============================
# Network Operations
# ===============================
SEND_EVENTS = {
    "EVENT_SEND",
    "EVENT_SENDTO",
    "EVENT_SENDMSG",
    "EVENT_WRITE_SOCKET_PARAMS",
}

RECEIVE_EVENTS = {
    "EVENT_RECV",
    "EVENT_RECVFROM",
    "EVENT_RECVMSG",
    "EVENT_READ_SOCKET_PARAMS",
}

CONNECT_EVENTS = {
    "EVENT_CONNECT",
}

ACCEPT_EVENTS = {
    "EVENT_ACCEPT",
}

BIND_EVENTS = {
    "EVENT_BIND",
}

LISTEN_EVENTS = {
    "EVENT_LISTEN",
}

