# Implementation Plan: Friendlier Empty List

**Branch**: `003-friendly-empty-list` | **Date**: 2026-10-02 | **Spec**: [spec.md](spec.md)

## Summary

Change the message `list_tasks` prints for an empty list, and update the test that asserts it.

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: standard library only
**Testing**: `unittest`

## Constitution Check

- I. Standard library only: pass.
- II. Every behavior has a test: pass (the empty-list test is updated).

## Project Structure

```text
todo.py
tests/test_todo.py
```
