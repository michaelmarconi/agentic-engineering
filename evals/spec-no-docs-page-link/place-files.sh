#!/usr/bin/env bash
set -eu
git init -q -b main
mkdir -p docs/specs src
cat > docs/brief.md <<'BRIEF'
---
type: Brief
---

# Tasks

## What it is

A small to-do app for one person, run in the browser.

## Who it is for

Anyone who wants a plain list of things to do.

## Why it exists

Most to-do apps ask for an account; this one keeps the list on the person's own device.

## Goals

- A new task can be added in under five seconds.

## Out of scope

- Sharing lists with other people.

## Constraints

- The list is kept in the browser's own storage; nothing is sent to a server.
BRIEF
cat > docs/architecture.md <<'ARCH'
# How the pieces fit together

The page shows one list. `src/tasks.ts` holds the list in memory and saves it to the browser's
local storage after every change. A task has a title, of 1 to 200 characters, and a done flag.
New tasks go to the top of the list.
ARCH
cat > src/tasks.ts <<'CODE'
export interface Task { title: string; done: boolean }
export const tasks: Task[] = [];
CODE
git add -A
git -c user.name=eval -c user.email=eval@example.com commit -q -m "Start"
