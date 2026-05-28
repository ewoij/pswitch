#!/usr/bin/env bash
current_session=$(tmux display-message -p '#{session_name}')
rel_path=$(pswitch list --relative --hide="$current_session" | fzf --no-sort --reverse) || exit 0
abs_path="$(pswitch config get dir)/$rel_path"

setup_session() {
  local session="$1" path="$2"
  if [ -f "$path/.venv/bin/activate" ]; then
    tmux send-keys -t "$session":0.0 "source .venv/bin/activate" Enter
  fi
  tmux send-keys -t "$session":0.0 "nvim" Enter ":NERDTree" Enter
  tmux split-window -h -t "$session":0.0 -c "$path"
  tmux select-pane -t "$session":0.0
}

if ! tmux has-session -t "$rel_path" 2>/dev/null; then
  tmux new-session -d -s "$rel_path" -c "$abs_path"
  setup_session "$rel_path" "$abs_path"
fi

tmux switch-client -t "$rel_path"
pswitch top "$abs_path"
