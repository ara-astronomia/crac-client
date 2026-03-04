# AGENTS.md - Development Guide for CRAC Client

This document provides comprehensive guidelines for any agent or developer working on the CRAC Client codebase. It is designed to be the single point of truth for project standards, GUI management, and communication with the CRAC Server.

## 1. Project Overview
CRAC Client is a desktop application providing a Graphical User Interface (GUI) for the CRAC observatory. It acts as a gRPC client, sending commands to and receiving status from the `crac-server`.

### Main Technologies
- **Language:** Python 3.10+
- **GUI Framework:** [FreeSimpleGUI](https://github.com/FreeSimpleGUI/FreeSimpleGUI) (fork of PySimpleGUI)
- **Communication:** gRPC using the `crac-protobuf` library.
- **Visualization:** [Plotly](https://plotly.com/python/) (for weather gauges) and [OpenCV](https://opencv.org/).
- **Dependency Management:** [uv](https://github.com/astral-sh/uv) (Migrated from Poetry).
- **Internationalization:** `gettext` for Italian localization.

---

## 2. Commands (using uv)

### Execution
**CRITICAL**: The application MUST be run from the `crac_client/` directory to ensure relative paths for `logging.conf`, configurations, and translations work correctly.

```bash
cd crac_client
uv run python app.py
```

### Testing
Run unit tests from the `crac_client/` folder:
```bash
# Example: Run gRPC channel unification tests
export PYTHONPATH=$PYTHONPATH:.
uv run python ../tests/unit/retriever/test_retriever_channels.py
```

### Localization
To compile the Italian localization (compile `.po` to `.mo`):
```bash
cd locales/it/LC_MESSAGES
msgfmt -o base.mo base
```

---

## 3. Architecture & Project Structure

The client follows an asynchronous, event-driven pattern to keep the UI responsive.

```
crac_client/
├── app.py                  # Entry point: Main GUI event loop and Job processor
├── gui.py                  # UI Definition: Layout, themes, and drawing logic
├── gui_constants.py        # Labels, Keys, and shared UI enums
├── jobs.py                 # Thread-safe queue (JOBS) for UI updates
├── config.py / config.ini  # Configuration management
├── loc.py                  # Localization helpers
├── retriever/              # gRPC communication layer (Async Futures)
│   ├── retriever.py        # Base class for all retrievers
│   ├── roof_retriever.py
│   └── ...
├── converter/              # Response parsing layer
│   ├── converter.py        # Base class for all converters
│   ├── weather_converter.py # Handles Plotly image generation
│   └── ...
└── locales/                # Translation files
```

---

## 4. Communication Pattern (The JOBS Queue)

To prevent the GUI from freezing during network calls:
1. **Request**: `app.py` triggers an action in a `Retriever`.
2. **Async Call**: The `Retriever` uses gRPC `future()` to call the server without blocking.
3. **Callback**: When the server responds, `Retriever.callback` is executed in a background thread.
4. **Queue**: The callback places a "job" (converter function + raw response) into the `JOBS` queue.
5. **UI Update**: The main loop in `app.py` polls the `JOBS` queue and executes the converter, which updates the `gui.py` elements.

---

## 5. Development Standards & Best Practices

### gRPC Channel Management
- **Shared Channel**: A single `grpc.insecure_channel` should be created in `app.py` and passed to all `Retriever` instances to save resources.
- **Async Safety**: Never update GUI elements (`window['key'].update()`) directly from a retriever callback. Always use the `JOBS` queue.

### Performance
- **Polling Frequency**: Defined by `sleep` in `config.ini`. Avoid very low values (< 500ms) to prevent queue flooding.
- **Plotly Gauges**: Generation of images is CPU intensive. Ensure they are only updated when the data actually changes.

### Code Style
- **Naming**: Consistent with the Server (snake_case).
- **Localization**: Use the `_()` helper for any user-facing string.
- **Error Handling**: `Retriever.callback` must handle `grpc.RpcError` gracefully to prevent thread crashes.

---

---

## 7. Agent Autonomy & Safeguards

To ensure efficiency and safety, the following rules apply to AI agents working on this project:

- **Autonomy**: Once a high-level plan is approved by the user, the agent is authorized to proceed through **Plan -> Act -> Validate** cycles without per-step confirmation.
- **Git User Email**: Always verify that `git config user.email` is set to `alkcxy@gmail.com` before making any commit.
- **No Remote Push**: Agents are **strictly forbidden** from executing `git push`. This action is reserved for the human user.
- **Mandatory Testing**: A commit can only be made if all relevant unit tests pass. 
- **Autonomous Fixes**: If tests fail after a modification, the agent should attempt up to **3 iterations** of autonomous fixing before stopping to consult the user.
- **Atomic Commits**: Prefer small, descriptive commits over large "catch-all" updates.
- **Strict Scope**: I am strictly forbidden from modifying any files or directories outside the explicitly authorized project directories without confirmation. I must NEVER delete an entire directory outside the work projects.

