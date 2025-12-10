# Common E2E Test Patterns

## Table of Contents
1. [Login Flow](#login-flow)
2. [Form Submission](#form-submission)
3. [Navigation Testing](#navigation-testing)
4. [Modal/Dialog Testing](#modaldialog-testing)
5. [List/Table Testing](#listtable-testing)
6. [Search and Filter](#search-and-filter)
7. [File Upload](#file-upload)
8. [Error State Verification](#error-state-verification)

---

## Login Flow

```python
async def test_login(runner):
    await runner.navigate("https://app.example.com/login")
    await runner.screenshot("login_page")
    
    # Fill credentials
    await runner.fill("label:Email", "user@example.com")
    await runner.fill("label:Password", "secure123")
    
    # Submit
    await runner.click("role:button[name=Log in]")
    
    # Verify redirect to dashboard
    await runner.wait_for("text:Welcome back", state="visible")
    await runner.screenshot("dashboard_after_login")
```

---

## Form Submission

```python
async def test_contact_form(runner):
    await runner.navigate("https://example.com/contact")
    
    # Fill text fields
    await runner.fill("label:Name", "John Doe")
    await runner.fill("label:Email", "john@example.com")
    await runner.fill("label:Message", "Hello, this is a test message.")
    
    # Select dropdown
    await runner.select_option("label:Subject", "Support")
    
    # Check checkbox
    await runner.check("role:checkbox[name=Subscribe to newsletter]")
    
    # Screenshot before submit
    await runner.screenshot("form_filled")
    
    # Submit form
    await runner.click("role:button[name=Send]")
    
    # Verify success
    await runner.wait_for("text:Thank you", state="visible")
    await runner.screenshot("form_success")
```

---

## Navigation Testing

```python
async def test_main_navigation(runner):
    await runner.navigate("https://example.com")
    
    # Test each nav link
    nav_items = [
        ("Products", "/products"),
        ("About", "/about"),
        ("Contact", "/contact"),
    ]
    
    for name, expected_path in nav_items:
        await runner.click(f"role:link[name={name}]")
        await runner.wait_for(f"text:{name}", state="visible")
        await runner.screenshot(f"nav_{name.lower()}")
        
    # Test mobile menu (if responsive)
    # await runner.click("role:button[name=Menu]")
    # await runner.screenshot("mobile_menu_open")
```

---

## Modal/Dialog Testing

```python
async def test_confirmation_dialog(runner):
    await runner.navigate("https://example.com/items")
    
    # Trigger delete action
    await runner.click("role:button[name=Delete]")
    
    # Wait for modal
    await runner.wait_for("role:dialog", state="visible")
    await runner.screenshot("delete_confirmation_modal")
    
    # Verify modal content
    text = await runner.get_text("role:dialog")
    assert "Are you sure" in text
    
    # Confirm deletion
    await runner.click("role:button[name=Confirm]")
    
    # Verify modal closed and item removed
    await runner.wait_for("role:dialog", state="hidden")
    await runner.screenshot("after_delete")
```

---

## List/Table Testing

```python
async def test_data_table(runner):
    await runner.navigate("https://example.com/users")
    await runner.wait_for("role:table", state="visible")
    await runner.screenshot("users_table")
    
    # Sort by column
    await runner.click("role:columnheader[name=Name]")
    await runner.screenshot("sorted_by_name")
    
    # Click row action
    await runner.click("role:row >> role:button[name=Edit]")
    await runner.wait_for("role:dialog", state="visible")
    await runner.screenshot("edit_user_modal")

async def test_infinite_scroll(runner):
    await runner.navigate("https://example.com/feed")
    await runner.screenshot("initial_items")
    
    # Scroll to load more
    await runner.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await runner.wait_for("css:.item:nth-child(20)", state="visible")
    await runner.screenshot("after_scroll", full_page=True)
```

---

## Search and Filter

```python
async def test_search(runner):
    await runner.navigate("https://example.com/products")
    
    # Enter search term
    await runner.fill("placeholder:Search products", "laptop")
    await runner.click("role:button[name=Search]")
    
    # Wait for results
    await runner.wait_for("text:results for", state="visible")
    await runner.screenshot("search_results")
    
    # Apply filter
    await runner.click("role:checkbox[name=In Stock]")
    await runner.wait_for("css:.loading", state="hidden")
    await runner.screenshot("filtered_results")
    
    # Clear filters
    await runner.click("role:button[name=Clear all]")
    await runner.screenshot("cleared_filters")
```

---

## File Upload

```python
async def test_file_upload(runner):
    await runner.navigate("https://example.com/upload")
    
    # Set file input (use page directly for file uploads)
    await runner.page.locator("input[type=file]").set_input_files("/path/to/file.pdf")
    
    # Verify file selected
    await runner.wait_for("text:file.pdf", state="visible")
    await runner.screenshot("file_selected")
    
    # Upload
    await runner.click("role:button[name=Upload]")
    await runner.wait_for("text:Upload complete", state="visible")
    await runner.screenshot("upload_success")
```

---

## Error State Verification

```python
async def test_form_validation_errors(runner):
    await runner.navigate("https://example.com/signup")
    
    # Submit empty form
    await runner.click("role:button[name=Sign up]")
    
    # Verify error messages
    await runner.wait_for("text:Email is required", state="visible")
    await runner.screenshot("validation_errors")
    
    # Fill invalid email
    await runner.fill("label:Email", "invalid-email")
    await runner.click("role:button[name=Sign up]")
    
    await runner.wait_for("text:Invalid email format", state="visible")
    await runner.screenshot("invalid_email_error")

async def test_api_error_handling(runner):
    await runner.navigate("https://example.com/dashboard")
    
    # Trigger action that fails
    await runner.click("role:button[name=Load data]")
    
    # Verify error toast/banner
    await runner.wait_for("role:alert", state="visible")
    await runner.screenshot("error_alert")
    
    error_text = await runner.get_text("role:alert")
    assert "error" in error_text.lower() or "failed" in error_text.lower()
```

---

## Screenshot Verification Workflow

After capturing screenshots, analyze them with Claude:

```python
async def analyze_screenshots(runner):
    """Get screenshots for Claude to analyze."""
    screenshots = runner.get_screenshots_for_analysis()
    
    # Each screenshot has:
    # - name: descriptive name
    # - path: file path
    # - base64: base64-encoded PNG
    
    for s in screenshots:
        # Send s['base64'] to Claude for visual verification
        # Claude can check:
        # - Layout correctness
        # - Text content
        # - Error states
        # - Visual regressions
        pass
    
    # After successful verification
    if all_tests_passed:
        runner.cleanup_screenshots()
```

---

## Best Practices

1. **Use role-based selectors** - Most resilient to UI changes
2. **Wait for specific states** - Don't use arbitrary sleeps
3. **Screenshot at key moments** - Before/after important actions
4. **Test user flows, not implementation** - Focus on behavior
5. **Clean up after success** - Remove temp screenshots
6. **Handle loading states** - Wait for spinners to disappear
7. **Test error paths** - Verify error handling works
