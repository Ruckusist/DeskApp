# Copilot-instructions:
Following are a set of guidlines and considerations.

User prompts are of a variety of types, and generally need to be exapanded upon
    before being implemented. in this way, you copilot are to elevate the prompt
    into a full fledged proposal every time. the user will ask for 3 types of
    work done.
    1) add a feature.
    2) review the feature proposal for soundness
    and files and functions touched or need to implement that feature, then,
    3) fix bugs in that feature.

# Changelog.ai:
    - this is how you comuniicate completeness of projects to yourself such that
    upon review you can see what has been done, and what is left to do.
    - always update the changelog upon completion of a proposal.
    - always credit yourself in the changelog for code changes.

## The Proposal System:

# in the case of 1) add a feature:
    - create a proposal folder in .github/proposals/
    - create a proposal file in that folder
    - write the proposal in that file

# Guidelines for Proposals
    - proposals should be numbered sequentially (Proposal 8, 9, 10, 11, etc.)
    - proposal numbers should match the feature/idea being implemented
    - keep a running list of proposal numbers to avoid conflicts
    - proposals should start every section with a checkbox.
    - proposals should be execututed using the checkboxes. mark them as you go.
    - proposals should be general and architectural.
    - proposals should not be about specific code changes.
    - proposals upon review should add the related document file paths and
        function names to be changed if applicable.
    - proposals should be written with the intent to be executed by an AI agent.
    - proposals should be reviewed and updated as needed.
    - should start every actionable item with a checkbox.
    - should be written with the intent to be executed by an AI agent.
    - filename pattern should be IdeaNum_IdeaTitle_MMDDYY.proposal
    - first line should be IdeaTitle_MMDDYY
    - next should be the last updated review date.
    - skip a line.
    - next should be the originating prompt.
    - next should be the interpretation of the prompt.
    - skip a line
    - next should be the full proposal.

# in the case of 2) review:
    - review the proposal file for soundness
    - add files and functions to be changed or added.
    - the AI being asked to review the code will likely be different than
      the one that wrote the proposal. so if the other guy is dead wrong, and
      you know it, say something, DENY the proposal and setup a better prompt
      that will return a result that is more likely to achieve the desired
      result.
    - maintain all documentation in the associated proposal file.

# in the case of 3) fix bugs:
    - OH WE are going to spend a lot of time here...

    - start a new document with the users prompt. title that document
        'BUGFIX_<ISSUE_NUMBER>_<RESOLVED/UNRESOLVED>.prop' in the
        .github/proposal/<current_feature>/ folder.
    - if the user reports a whole bunch of bugs at once break up the ideas and
        look them up seperately for overlap, incase they have been reported
        previously.
    - the bug will remain unresolved until the user confirms it is resolved.
    - once the user confirms it is resolved, change the file name to
        'BUGFIX_<ISSUE_NUMBER>_RESOLVED.prop'
    - the bugfix proposal should contain:
        - the users prompt
        - your interpretation of the prompt
        - a list of files and functions to be changed/ that were changed.

# in the case of 4) implement the proposal:
    - follow the proposal file to the letter.
    - make sure to credit the proposal in the changelog and in the code comments
      where applicable.
    - always keep functions small and files small.
    - always use classes.
    - always use 4 spaces for indentation, never tabs.
    - always use double quotes for strings, never single quotes.
    - always use CamelCase for function and variable names.
    - never use an underscore _ at the beginning of function or variable names.
    - always keep everything to 79 characters per line.
    - always think in a unix way.
    - always prefer building our own tools.
    - always work in complete sections. Do not leave half done code.


# Project Conventions

    - 80 characters per line max.
    - use 4 spaces for indentation, never tabs.
    - Always credit your changes in the file and in the changelog.
    - focus: sidedesk/ by default. If user says otherwise, confirm first.
    - we dont like _ at the beginning of function or variable names.
    - we use 4 spaces for indentation, never tabs.
    - we use CamelCase for function and variable names.
    - we keep everything to 79 characters per line.
    - we use double quotes for strings, never single quotes.
    - we prefer python classes.
    - we keep functions small and files small.
    - we think in a unix way.
    - we prefer building our own tools.
    - we work in complete sections. Do not leave half done code.
    - we always work from a plan.
    - keep all notes here in the .github folder. keep notes in working proposal files.
    - always follow the above conventions.
    - leave the documentation to another bot. dont do it. just keep working.
    - always roll the version for code changes; every time.
    - DONT EVER change a file in the venv folder. wtf.
    - SIMPLE. STREAMLINED. EFFICIENT. MINIMAL.
    - the bash command, 'werk' will put you into the venv. this is good.
    - always roll the version on completeion of proposal.
    - always update the changelog on completion of proposal.
    - always update the proposal file on completion of proposal.

# Versioning
    - APP_RELEASE . <FEATURE_PROPOSAL_NUMBER> . <BUGFIX_NUMBER>

    ALWAYS ROLL THE VERSION ON ANY CODE CHANGE.
    - example: 1.20.0 - initial planning phase of Proposal 20
    - example: 1.20.1 - first implementation for Proposal 20
    - example: 1.20.2 - bugfix for Proposal 20


# ACCEPTING NEW PROJECTS
    Below this poing is project metadata. is only valueable to you. use it. make
    notes. add to it as needed for your own use. I have addeda few fields that
    may or may not be useful to you. feel free to modify as needed. if your prompt
    says something like, rebuild your project area or something like that, go
    through this area and bring it inline with what the user wants you to focus
    on.


# Project Metadata

Project Focus: Deskapp
Root folder: /home/ruckus/code/DeskApp
changelog: /home/ruckus/code/deskapp/.github/changelog.ai
proposals: /home/ruckus/code/deskapp/.github/proposals/
virtual environment: source .venv/bin/activate
