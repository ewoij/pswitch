#!/usr/bin/env bash
current_session=$(tmux display-message -p '#{session_name}')
rel_path=$(pswitch list --relative --hide="$current_session" | fzf --no-sort --reverse) || exit 0
abs_path="$(pswitch config get dir)/$rel_path"

tmux new-session -s "$rel_path" -c "$abs_path" -d || true
tmux switch-client -t "$rel_path"
pswitch top "$abs_path"
