#!/usr/bin/env bash

TRIAGE_PATH=~/code/github/hernamesbarbara/triage

echo -e "cd $TRIAGE_PATH\n"
cd "$TRIAGE_PATH"

echo -e "Triaging new files...\n"

python -m cli.triage linkedin "$LINKEDIN_DATA_PATH"

cd -

echo -e "done\n"
exit 0
