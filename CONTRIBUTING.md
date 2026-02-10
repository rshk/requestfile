# Contributing to requestfile

Contributions are welcome.

Since the current state of the project is **very** experimental and
subject to change, I recommend getting in touch before setting off to
write a large PR!

## Code linting

Please use:

```
# Format code (required)
ruff format .

# Sort imports (required)
ruff check --select I --fix .

# This usually does a good job cleaning things up,
# but please double check!
ruff check --fix .
```
