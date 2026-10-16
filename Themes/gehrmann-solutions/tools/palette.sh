#!/bin/bash
# Shown in the preview screenshot (tools/preview.sh): the terminal colours, the theme folder and its last commit.
cd "${1:-$PWD}"
clear
names=(black red green yellow blue magenta cyan white)
title="Gehrmann Solutions"; [[ $PWD == *-light ]] && title="Gehrmann Solutions Light"
printf '\n  \e[1m%s\e[0m  terminal colours\n\n' "$title"
for i in 0 1 2 3 4 5 6 7; do
  printf '  %-8s \e[3%dmnormal\e[0m  \e[9%dmbright\e[0m  \e[4%dm      \e[0m \e[10%dm      \e[0m\n' "${names[$i]}" $i $i $i $i
done
printf '\n'
eza -l --no-user --no-time --no-filesize --icons --group-directories-first
printf '\n'
git log --oneline --graph --decorate -3 2>/dev/null
printf '\n'
exec bash --norc --noprofile -i
