UNHINGED
========

Graph-based workflow engine. Voice-first terminal interface.

START

    ./unhinged              TUI
    ./unhinged dev          Dev commands

LAYOUT

    cli/                    Commands
    libs/python/graph/      Graph engine
    libs/python/terminal/   TUI renderer
    services/               AI services
    man/                    Man pages

TUI

    User Terminal           Daily tasks
    Sudoers Terminal        Elevated mode
    Graphs                  Workflow editor
    Prompts                 Prompt library
    Codex                   Node reference

NODES

    unix                    Shell
    llm                     Generation
    human_feedback          Approval
    structured_llm          JSON output
    web_search              Search
    recall                  Vector recall

COMMANDS

    unhinged tui            Terminal interface
    unhinged graph list     List graphs
    unhinged graph run ID   Execute graph
    unhinged dev build      Build
    unhinged dev lint       Lint
    unhinged system status  Health

SEE ALSO

    man unhinged
    man unhinged-graph

---
Davis | Swartz | Turing
