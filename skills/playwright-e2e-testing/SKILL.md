---
name: playwright-e2e-testing
description: "Frontend end-to-end feature testing using Playwright with Chrome. Opens Chrome browser, interacts with web pages based on feature requirements, captures screenshots at key points, analyzes results visually, and cleans up screenshots after successful verification. Use this skill when asked to test a web application feature end-to-end, verify UI functionality by interacting with and screenshotting a page, automate browser testing with visual verification, check if a frontend feature works correctly, or debug UI issues by capturing screenshots during interaction."
---

# Playwright E2E Feature Testing

Test frontend features by launching Chrome, interacting with the page, capturing screenshots for visual analysis, and cleaning up after verification.

## Quick Start

```python
import asyncio
from run_e2e_test import E2ETestRunner

async def test_feature():
    runner = E2ETestRunner(headless=False, background=True)  # background=True prevents focus stealing
    await runner.setup()
    
    try:
        # 1. Navigate to page
        await runner.navigate("https://example.com")
        
        # 2. Interact with elements
        await runner.fill("label:Email", "test@example.com")
        await runner.click("role:button[name=Submit]")
        
        # 3. Capture screenshots
        await runner.screenshot("after_submit")
        
        # 4. Get screenshots for analysis
        screenshots = runner.get_screenshots_for_analysis()
        # Each has: name, path, base64 (for Claude vision analysis)
        
        # 5. After successful verification, cleanup
        runner.cleanup_screenshots()
    finally:
        await runner.teardown()

asyncio.run(test_feature())
```

## Installation

```bash
pip install playwright --break-system-packages
playwright install chromium
```

## Workflow

1. **Setup**: Install Playwright, create `E2ETestRunner` instance
2. **Navigate**: Go to the target URL
3. **Interact**: Click, fill, select, hover based on feature requirements
4. **Screenshot**: Capture at key verification points
5. **Analyze**: Review screenshots (Claude can analyze base64 images)
6. **Cleanup**: Delete screenshots after successful verification

## Selector Strategies (Priority Order)

| Strategy | Syntax | Example |
|----------|--------|---------|
| Role (best) | `role:type[name=X]` | `role:button[name=Submit]` |
| Label | `label:X` | `label:Email` |
| Placeholder | `placeholder:X` | `placeholder:Search` |
| Test ID | `testid:X` | `testid:submit-btn` |
| Text | `text:X` | `text:Welcome` |
| CSS (last resort) | `css:X` or `.class` | `css:.btn-primary` |

## Core Actions

```python
# Navigation
await runner.navigate(url)

# Input
await runner.fill(selector, value)       # Fast fill
await runner.type_text(selector, text)   # Character by character
await runner.select_option(selector, value)
await runner.check(selector)
await runner.uncheck(selector)

# Mouse
await runner.click(selector)
await runner.hover(selector)

# Wait
await runner.wait_for(selector, state="visible")  # visible, hidden, attached

# Read
text = await runner.get_text(selector)
attr = await runner.get_attribute(selector, "href")
visible = await runner.is_visible(selector)
```

## Screenshots

```python
# Page screenshot
path = await runner.screenshot("name")

# Full scrollable page
path = await runner.screenshot("name", full_page=True)

# Element only
path = await runner.screenshot("name", selector="css:.error-msg")

# Get base64 for Claude analysis
screenshots = runner.get_screenshots_for_analysis()
# Returns: [{"name": "...", "path": "...", "base64": "..."}]

# Cleanup after verification
runner.cleanup_screenshots()
```

## Example: Login Feature Test

```python
async def test_login_feature(runner):
    await runner.navigate("https://app.example.com/login")
    await runner.screenshot("01_login_page")
    
    await runner.fill("label:Email", "user@test.com")
    await runner.fill("label:Password", "password123")
    await runner.screenshot("02_credentials_filled")
    
    await runner.click("role:button[name=Sign in]")
    await runner.wait_for("text:Dashboard", state="visible")
    await runner.screenshot("03_dashboard")
    
    # Analyze screenshots, then cleanup
    runner.cleanup_screenshots()
```

## References

- [API Reference](references/api_reference.md) - Full API documentation
- [Test Patterns](references/test_patterns.md) - Common testing scenarios

## Key Principles

1. **Use role selectors** - Most resilient to UI changes
2. **Wait for states** - Use `wait_for` instead of sleep
3. **Screenshot key moments** - Before/after important actions
4. **Test user behavior** - Not implementation details
5. **Cleanup on success** - Remove temp files after verification
