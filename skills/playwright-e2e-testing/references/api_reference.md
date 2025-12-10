# Playwright E2E Testing API Reference

## Table of Contents
1. [Locator Strategies](#locator-strategies)
2. [Actions](#actions)
3. [Assertions](#assertions)
4. [Screenshot Methods](#screenshot-methods)
5. [Browser Configuration](#browser-configuration)

---

## Locator Strategies

Use these prefixes in selectors to specify locator type:

| Prefix | Example | Description |
|--------|---------|-------------|
| `role:` | `role:button[name=Submit]` | Locate by ARIA role (recommended) |
| `text:` | `text:Welcome` | Locate by text content |
| `label:` | `label:Email` | Locate by associated label |
| `placeholder:` | `placeholder:Enter name` | Locate by placeholder attribute |
| `testid:` | `testid:submit-btn` | Locate by data-testid attribute |
| `css:` | `css:.class-name` | CSS selector |
| `xpath:` | `xpath://div[@id='main']` | XPath selector |
| (none) | `#id` or `.class` | Auto-detect (CSS default) |

### Recommended Priority
1. `role:` - Most resilient, tests user-visible behavior
2. `label:` / `placeholder:` - User-facing attributes
3. `testid:` - Explicit contracts for testing
4. `text:` - Content-based (may change with i18n)
5. `css:` / `xpath:` - Last resort, brittle

### Role Locator Options
```
role:button[name=Submit]           # Exact name match
role:textbox[name=Email]           # Input by accessible name
role:link[name=Learn more]         # Link by text
role:heading[level=1]              # H1 heading
role:checkbox[name=Accept terms]   # Checkbox
role:listitem                      # List items
```

---

## Actions

### Navigation
```python
# Basic navigation (returns result dict)
nav_result = await runner.navigate("https://example.com")

# Check if navigation succeeded
if not nav_result["success"]:
    print(nav_result["error"])       # Human-readable error
    print(nav_result["error_type"])  # e.g., "connection_refused", "timeout"
    print(nav_result["diagnostics"]) # Console errors, failed requests

# With custom wait strategy
nav_result = await runner.navigate(
    "https://example.com",
    wait_until="domcontentloaded"  # "load", "domcontentloaded", "networkidle"
)
```

### Click
```python
await runner.click("role:button[name=Submit]")
await runner.click("#submit-btn", force=True)  # Bypass actionability checks
```

### Text Input
```python
await runner.fill("role:textbox[name=Email]", "user@example.com")  # Fast fill
await runner.type_text("css:#search", "query", delay=100)  # Character by character
```

### Form Controls
```python
await runner.select_option("css:#country", "US")    # Dropdown
await runner.check("role:checkbox[name=Accept]")    # Check
await runner.uncheck("role:checkbox[name=Accept]")  # Uncheck
```

### Mouse
```python
await runner.hover("css:.menu-item")  # Hover to reveal submenu
await runner.click("role:button[name=Delete]", click_count=2)  # Double-click
```

### Waiting
```python
await runner.wait_for("css:.loading", state="hidden")   # Wait for element to hide
await runner.wait_for("text:Success", state="visible")  # Wait for element to appear
```

### Reading Values
```python
text = await runner.get_text("css:.message")           # Get text content
href = await runner.get_attribute("css:a.link", "href") # Get attribute
visible = await runner.is_visible("css:.modal")        # Check visibility
```

---

## Assertions

### Web-First Assertions (Recommended)
These auto-wait and retry until condition is met:

```python
# In test code using expect:
await expect(page.get_by_text("Success")).to_be_visible()
await expect(page.get_by_role("button")).to_be_enabled()
await expect(page.locator(".status")).to_have_text("Complete")
await expect(page.locator("input")).to_have_value("expected")
await expect(page).to_have_title("Dashboard")
await expect(page).to_have_url(/.*dashboard/)
```

### Common Assertions
| Method | Description |
|--------|-------------|
| `to_be_visible()` | Element is visible |
| `to_be_hidden()` | Element is hidden |
| `to_be_enabled()` | Form control is enabled |
| `to_be_disabled()` | Form control is disabled |
| `to_be_checked()` | Checkbox/radio is checked |
| `to_have_text(text)` | Element has exact text |
| `to_contain_text(text)` | Element contains text |
| `to_have_value(value)` | Input has value |
| `to_have_attribute(name, value)` | Element has attribute |
| `to_have_count(n)` | Locator matches n elements |

---

## Screenshot Methods

### Page Screenshot
```python
# Save to file
path = await runner.screenshot("login_page")

# Full scrollable page
path = await runner.screenshot("full_page", full_page=True)

# Get as base64 for analysis
b64 = await runner.screenshot_to_base64()
```

### Element Screenshot
```python
# Screenshot specific element
path = await runner.screenshot("error_message", selector="css:.error")
```

### Analysis Workflow
```python
# After test steps, get all screenshots
screenshots = runner.get_screenshots_for_analysis()
for s in screenshots:
    print(f"Name: {s['name']}")
    print(f"Base64: {s['base64'][:100]}...")  # For Claude analysis

# After successful verification
runner.cleanup_screenshots()  # Delete all temp files
```

---

## Browser Configuration

### Launch Options
```python
runner = E2ETestRunner(
    headless=False,           # Show browser window (True for CI)
    screenshot_dir="/tmp/ss", # Where to save screenshots
    timeout=30000,            # Default timeout in ms
    viewport_width=1280,      # Browser width
    viewport_height=720,      # Browser height
)
```

### Browser Channels
| Value | Browser |
|-------|---------|
| `None` | Bundled Chromium (default headless) |
| `"chrome"` | Google Chrome |
| `"chrome-beta"` | Chrome Beta |
| `"msedge"` | Microsoft Edge |
| `"msedge-dev"` | Edge Dev |

### Headless vs Headed
- **Headless** (`headless=True`): Faster, no GUI, ideal for CI
- **Headed** (`headless=False`): Visual debugging, see browser actions

---

## Error Handling & Diagnostics

### Navigation Errors
The `navigate()` method returns a result dict instead of throwing on common errors:

```python
nav_result = await runner.navigate("http://localhost:3000")

# Result structure:
{
    "success": True/False,
    "url": "http://localhost:3000",
    "error": "Connection refused: Server not running...",  # if failed
    "error_type": "connection_refused",  # categorized error type
    "status_code": 404,  # for HTTP errors
    "diagnostics": {...}  # console errors, failed requests
}
```

### Error Types
| Type | Description |
|------|-------------|
| `connection_refused` | Server not running or rejecting connections |
| `dns_error` | Could not resolve hostname |
| `ssl_error` | SSL/TLS certificate problem |
| `timeout` | Page did not load in time |
| `connection_timeout` | Server did not respond |
| `no_internet` | No network connection |
| `navigation_error` | Other navigation failures |

### Diagnostics API
```python
# Check for collected errors
if runner.has_errors():
    diagnostics = runner.get_diagnostics()

# Diagnostics structure:
{
    "console_errors": [{"type": "error", "text": "...", "location": "..."}],
    "failed_requests": [{"url": "...", "method": "GET", "failure": "..."}],
    "response_errors": [{"url": "...", "status": 404, "status_text": "Not Found"}],
    "page_errors": ["Uncaught TypeError: ..."]
}

# Clear diagnostics before a new test phase
runner.clear_diagnostics()
```

### Safe Action Wrapper
Wrap any action with error handling and automatic screenshot on failure:

```python
result = await runner.safe_action(
    "click_submit",
    runner.click("role:button[name=Submit]")
)
if not result["success"]:
    print(result["error"])       # Error message
    print(result["error_type"])  # "timeout", "playwright_error", etc.
    # Screenshot auto-captured as click_submit_error.png
```

### Automatic Screenshot on Errors
Screenshots are automatically captured for:
- Navigation timeouts → `ERROR_navigation_timeout.png`
- Navigation errors → `ERROR_navigation_error.png`
- Action timeouts → `TIMEOUT_{step_name}.png`
- Action errors → `ERROR_{step_name}.png`
- General failures → `FAILURE_{step_name}.png`

---

## Test Step JSON Format

For automated test execution via `--steps`:

```json
[
  {"action": "navigate", "params": {"url": "https://example.com"}},
  {"action": "fill", "params": {"selector": "label:Email", "value": "test@test.com"}},
  {"action": "fill", "params": {"selector": "label:Password", "value": "secret123"}},
  {"action": "click", "params": {"selector": "role:button[name=Log in]"}},
  {"action": "wait", "params": {"selector": "text:Welcome", "state": "visible"}},
  {"action": "screenshot", "params": {"name": "logged_in_dashboard", "full_page": true}},
  {"action": "pause", "params": {"seconds": 2}}
]
```

### Available Actions
| Action | Required Params | Optional Params |
|--------|----------------|-----------------|
| `navigate` | `url` | |
| `click` | `selector` | `options: {force, click_count}` |
| `fill` | `selector`, `value` | |
| `type` | `selector`, `text` | `delay` |
| `select` | `selector`, `value` | |
| `check` | `selector` | |
| `uncheck` | `selector` | |
| `hover` | `selector` | |
| `wait` | `selector` | `state` |
| `screenshot` | | `name`, `full_page`, `selector` |
| `pause` | | `seconds` |
