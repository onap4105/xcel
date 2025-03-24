Here's a clear comparison between `raise SystemExit(1)` and `sys.exit(1)` in Python:

### Key Differences

| Feature               | `raise SystemExit(1)`                     | `sys.exit(1)`                     |
|-----------------------|------------------------------------------|-----------------------------------|
| **Origin**            | Built-in exception                      | Function in `sys` module          |
| **Implementation**    | Direct exception raising                | Wrapper for `SystemExit`          |
| **Import Required**   | No (`SystemExit` always available)      | Requires `import sys`             |
| **Readability**       | More explicit about exception nature    | More conventional/idiomatic       |
| **Common Usage**      | Lower-level code                       | Application-level code            |
| **Exit Process**      | Yes (when uncaught)                     | Yes                               |
| **Traceback**         | Shows unless caught                     | Shows unless caught               |

### Technical Behavior

1. **Under the Hood**:
   ```python
   # sys.exit() is literally just:
   def exit(status=0):
       raise SystemExit(status)
   ```

2. **Exception Handling**:
   ```python
   try:
       sys.exit(1)  # Can be caught as SystemExit
   except SystemExit:
       print("Caught!")  # This will execute
   ```

3. **Cleanup Behavior**:
   Both trigger:
   - `finally` blocks
   - Context manager `__exit__` methods
   - Destructors (`__del__`)

### When to Use Which

**Use `sys.exit(1)` when:**
- Writing application code
- You want conventional/readable exits
- Working with other developers' expectations

**Use `raise SystemExit(1)` when:**
- Writing low-level/library code
- You need to exit from exception handlers
- Explicitly showing it's an exception

### Best Practice Example

```python
import sys

def main():
    try:
        # Application logic...
        if error_condition:
            sys.exit(1)  # Conventional application exit
            
    except SomeError:
        raise SystemExit(1)  # Explicit exception-based exit

if __name__ == "__main__":
    main()
```

### Special Cases

1. **In Interactive Shell**:
   - Both allow continued session if caught
   ```python
   >>> try: sys.exit()
   ... except SystemExit: print("Ignored")
   Ignored
   ```

2. **Exit Codes**:
   ```python
   sys.exit("Error message")  # Prints to stderr and exits with code 1
   raise SystemExit("Error")   # Same behavior
   ```

3. **Threads**:
   - Neither actually exits the process when called from non-main thread
   - Only exits the current thread

### Performance
- Identical (after module import for `sys`) - both compile to same bytecode
- `sys.exit()` adds one extra function call overhead

### Recommendation
For your copyright updater script, **use `sys.exit()`** because:
1. It's more conventional for CLI applications
2. Clearly communicates intent
3. Matches other Python tools' behavior
4. Requires no extra explanation for most Python developers

Example modification for your script:
```python
import sys

def load_config():
    try:
        # ... config loading ...
    except FileNotFoundError:
        logging.error("Config file missing")
        sys.exit(1)  # Changed from raise SystemExit
```
