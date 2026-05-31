# Copilot Instructions

Every user prompt is a work request. Expand the prompt into a full proposal
before acting. There are 4 work types:
    1) add a feature
    2) review a proposal
    3) fix a bug
    4) implement a proposal


# Changelog

- changelog lives at .github/changelog.ai
- update the changelog on completion of any work type
- credit yourself by model name in every changelog entry
- the changelog is how agents communicate state across sessions


# Proposals

## TODO Pipeline

New ideas that are not immediately executed enter as TODO files.
TODOs have no proposal number and do not affect versioning.

    - filename pattern: TODO_<Title>_<MMDDYY>.prop
    - same format as a proposal (originating prompt, interpretation, body)
    - NO checkboxes until the TODO is promoted to a numbered proposal
    - TODOs live in .github/proposals/ alongside numbered proposals
    - a TODO is promoted to a PROPOSAL when the user says to execute it:
        1. assign the next sequential proposal number
        2. rename: TODO_<Title>.prop → PROPOSAL_<NUM>_<Title>_<MMDDYY>.prop
        3. add checkboxes to every actionable item
        4. begin execution

The proposal number is locked at promotion time, not at idea time.
This ensures version numbers stay in sync with what was actually built.

## 1) Add a Feature
    - if the feature is to be executed now: create a numbered proposal
    - if the feature is a future idea: create a TODO file instead
    - proposals are numbered sequentially and globally; never reuse a number
    - proposal number must match the middle segment of the version number
    - filename pattern: PROPOSAL_<NUM>_<Title>_<MMDDYY>.prop
    - every actionable item starts with a checkbox
    - execute the proposal using the checkboxes; mark them as you go
    - proposals are architectural and behavioral; not line-by-line code edits
    - proposals are written to be executed by an AI agent

## Proposal File Format
    Line 1:  <Title>_<MMDDYY>
    Line 2:  Last reviewed: <MMDDYY>
    (blank)
    Originating Prompt: <exact user prompt>
    Interpretation: <your expansion of intent and scope>
    (blank)
    <full proposal with checkboxes>

## 2) Review a Proposal
    - review the proposal file for soundness and feasibility
    - add expected file paths and function names to be changed
    - the reviewing agent may differ from the authoring agent
    - if the proposal is wrong, DENY it explicitly and provide a corrected
      direction; do not implement a flawed plan
    - all review notes stay in the proposal file

## 3) Fix a Bug
    - create a bugfix artifact in the proposal folder for the affected feature
    - filename: BUGFIX_<NUM>_UNRESOLVED.prop
    - if multiple bugs are reported at once, check for shared root causes
      before treating them as independent
    - the bug stays UNRESOLVED until the user explicitly confirms it is fixed
    - on confirmation, rename to: BUGFIX_<NUM>_RESOLVED.prop
    - bugfix artifact contains:
        - the users prompt (verbatim)
        - your interpretation
        - list of files and functions changed or under investigation

## 4) Implement a Proposal
    - follow the proposal to the letter
    - credit the proposal number in the changelog
    - keep proposal checkboxes current throughout the session
    - roll the version and update the changelog before the session ends


# Project Conventions

    - 4 spaces for indentation, never tabs
    - double quotes for strings, never single quotes
    - CamelCase for all function and variable names
    - no leading underscores on names (dunders are fine)
    - 79 characters per line max
    - prefer classes for stateful and domain-modeling work
    - keep functions small; keep files small
    - work in complete sections; do not leave partial implementations
    - think in a unix way: one thing, done well, composable
    - prefer building our own tools
    - always work from a plan
    - do not generate documentation unless explicitly requested
    - do not touch anything inside .venv/
    - SIMPLE. STREAMLINED. EFFICIENT. MINIMAL.
    - the bash alias 'werk' activates the venv


# Versioning

    - version format: APP_RELEASE.PROPOSAL_NUMBER.BUGFIX_NUMBER
    - pyproject.toml is the single source of truth for the version
    - roll the version on every code change
    - example: 1.8.0  initial implementation of Proposal 8
    - example: 1.8.1  first confirmed bugfix under Proposal 8
    - example: 1.9.0  initial implementation of Proposal 9


# Project Metadata

Project Focus : Deskapp
Root Folder   : /home/dude/desk
Changelog     : .github/changelog.ai
Proposals     : .github/proposals/
Venv          : source .venv/bin/activate  (alias: werk)
Build Config  : pyproject.toml (authoritative)
