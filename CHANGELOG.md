# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.1] - 2026-04-14

### Fixed

- **Mathematica Backend: Print output not captured** - Print statements now correctly return output. Uses `EvaluationData[]` to capture Print output.

- **Mathematica Backend: Variable substitution incomplete** - Variables now correctly expand in output. Note: Users should avoid using built-in Mathematica symbol names (like `Re`, `Im`, `N`, `D`, `I`, `E`, `Pi`) as variable names.

- **Mathematica Backend: N[] function sometimes ineffective** - Numerical conversion now works reliably through proper output formatting.

- **Mathematica Backend: Grid no output** - Grid, TableForm, MatrixForm and other formatting functions now correctly display output.

- **Mathematica Backend: Variables undefined in compound expressions** - Multiple statements in a single code block now evaluate correctly.

- **Mathematica Backend: Scientific notation display issues** - Numbers now display in proper format.

- **Mathematica Backend: Variables persist after Clear["Global`*"]** - The `reset()` method now properly clears all variables using ClearAll + Remove + context rebuild.

- **Mathematica Backend: Conditional expressions in Table/Do loops** - If/Which conditionals now evaluate correctly in loop structures.

### Changed

- **Mathematica Backend**: Rewrote `evaluate()` method to use `EvaluationData[]` for capturing both Print output and computation results.

- **Mathematica Backend**: Updated `_process_result()` to parse tuple-format return data from Mathematica.

- **Tests**: Updated `test_manager.py` and `test_octave.py` to match current API.

### Technical Details

The core fix uses Mathematica's `EvaluationData[]` function:

```mathematica
Module[{evalData},
  evalData = EvaluationData[user_code];
  {
    {"type", "text"},
    {"outputLog", evalData["OutputLog"]},
    {"messages", evalData["MessagesText"]},
    {"data", ToString[OutputForm[evalData["Result"]]]}
  }
]
```

This captures:
- `OutputLog`: All Print output
- `Result`: The final computation result
- `MessagesText`: Any warning/error messages

## [1.0.0] - 2026-03-18

### Added

- Initial release
- Support for Mathematica, SageMath, Octave, R, Python Scientific, MATLAB backends
- MCP server with compute, list_backends, stop, doc tools
- Documentation for each backend
