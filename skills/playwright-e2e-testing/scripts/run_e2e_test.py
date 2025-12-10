#!/usr/bin/env python3
"""
Playwright E2E Feature Test Runner

Launches Chrome, executes test steps, captures screenshots for analysis,
and cleans up after successful verification.
"""

import asyncio
import argparse
import json
import base64
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext


class E2ETestRunner:
    """Executes E2E feature tests with screenshot capture and analysis."""
    
    def __init__(
        self,
        headless: bool = False,
        screenshot_dir: str = "/tmp/e2e_screenshots",
        timeout: int = 30000,
        viewport_width: int = 1280,
        viewport_height: int = 720,
        background: bool = False,
    ):
        self.headless = headless
        self.background = background
        self.screenshot_dir = Path(screenshot_dir)
        self.timeout = timeout
        self.viewport = {"width": viewport_width, "height": viewport_height}
        self.screenshots: list[Path] = []
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
    async def setup(self) -> None:
        """Initialize browser and page."""
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        playwright = await async_playwright().start()

        # Build launch args based on mode
        if self.headless:
            launch_args = ["--no-sandbox", "--disable-dev-shm-usage"]
        elif self.background:
            # Position window off-screen to prevent focus stealing
            launch_args = ["--window-position=-9999,-9999"]
        else:
            launch_args = []

        # Launch Chrome (chromium channel for real Chrome, or bundled chromium)
        self.browser = await playwright.chromium.launch(
            headless=self.headless,
            channel="chrome" if not self.headless else None,
            args=launch_args,
        )
        
        self.context = await self.browser.new_context(
            viewport=self.viewport,
            locale="en-US",
        )
        self.context.set_default_timeout(self.timeout)
        self.page = await self.context.new_page()
        
    async def teardown(self) -> None:
        """Clean up browser resources."""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
            
    async def navigate(self, url: str) -> None:
        """Navigate to URL and wait for load."""
        await self.page.goto(url, wait_until="networkidle")
        
    async def click(self, selector: str, **kwargs) -> None:
        """Click an element using various selector strategies."""
        locator = self._get_locator(selector)
        await locator.click(**kwargs)
        
    async def fill(self, selector: str, value: str) -> None:
        """Fill a text input field."""
        locator = self._get_locator(selector)
        await locator.fill(value)
        
    async def type_text(self, selector: str, text: str, delay: int = 50) -> None:
        """Type text character by character (for special keyboard handling)."""
        locator = self._get_locator(selector)
        await locator.press_sequentially(text, delay=delay)
        
    async def select_option(self, selector: str, value: str) -> None:
        """Select an option from a dropdown."""
        locator = self._get_locator(selector)
        await locator.select_option(value)
        
    async def check(self, selector: str) -> None:
        """Check a checkbox or radio button."""
        locator = self._get_locator(selector)
        await locator.check()
        
    async def uncheck(self, selector: str) -> None:
        """Uncheck a checkbox."""
        locator = self._get_locator(selector)
        await locator.uncheck()
        
    async def hover(self, selector: str) -> None:
        """Hover over an element."""
        locator = self._get_locator(selector)
        await locator.hover()
        
    async def wait_for(self, selector: str, state: str = "visible") -> None:
        """Wait for element to reach specified state."""
        locator = self._get_locator(selector)
        await locator.wait_for(state=state)
        
    async def get_text(self, selector: str) -> str:
        """Get text content of an element."""
        locator = self._get_locator(selector)
        return await locator.text_content() or ""
        
    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Get attribute value of an element."""
        locator = self._get_locator(selector)
        return await locator.get_attribute(attribute)
        
    async def is_visible(self, selector: str) -> bool:
        """Check if element is visible."""
        locator = self._get_locator(selector)
        return await locator.is_visible()
        
    async def screenshot(
        self,
        name: str,
        full_page: bool = False,
        selector: Optional[str] = None,
    ) -> Path:
        """
        Capture screenshot for later analysis.
        
        Args:
            name: Descriptive name for the screenshot
            full_page: Capture full scrollable page
            selector: Optional selector to screenshot specific element
            
        Returns:
            Path to saved screenshot
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)
        filename = f"{timestamp}_{safe_name}.png"
        filepath = self.screenshot_dir / filename
        
        if selector:
            locator = self._get_locator(selector)
            await locator.screenshot(path=str(filepath))
        else:
            await self.page.screenshot(path=str(filepath), full_page=full_page)
            
        self.screenshots.append(filepath)
        return filepath
        
    async def screenshot_to_base64(
        self,
        full_page: bool = False,
        selector: Optional[str] = None,
    ) -> str:
        """
        Capture screenshot and return as base64 for direct analysis.
        
        Returns:
            Base64-encoded PNG image
        """
        if selector:
            locator = self._get_locator(selector)
            buffer = await locator.screenshot()
        else:
            buffer = await self.page.screenshot(full_page=full_page)
            
        return base64.b64encode(buffer).decode("utf-8")
        
    def get_screenshots_for_analysis(self) -> list[dict]:
        """
        Get all captured screenshots as base64 for Claude analysis.
        
        Returns:
            List of dicts with name and base64 data
        """
        results = []
        for path in self.screenshots:
            if path.exists():
                with open(path, "rb") as f:
                    data = base64.b64encode(f.read()).decode("utf-8")
                results.append({
                    "name": path.stem,
                    "path": str(path),
                    "base64": data,
                })
        return results
        
    def cleanup_screenshots(self) -> None:
        """Delete all captured screenshots after successful verification."""
        for path in self.screenshots:
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass
        self.screenshots.clear()
        
        # Try to remove directory if empty
        try:
            self.screenshot_dir.rmdir()
        except OSError:
            pass
            
    def _get_locator(self, selector: str):
        """
        Get locator from selector string.
        
        Supports multiple selector strategies:
        - role:button[name=Submit] -> getByRole
        - text:Welcome -> getByText
        - label:Email -> getByLabel
        - placeholder:Enter name -> getByPlaceholder
        - testid:submit-btn -> getByTestId
        - css:.class or #id -> CSS selector
        - xpath://div -> XPath selector
        - Default: CSS selector
        """
        if selector.startswith("role:"):
            # Parse role:button[name=Submit]
            role_part = selector[5:]
            if "[" in role_part:
                role, attrs = role_part.split("[", 1)
                attrs = attrs.rstrip("]")
                options = {}
                for attr in attrs.split(","):
                    key, val = attr.split("=", 1)
                    options[key.strip()] = val.strip().strip("'\"")
                return self.page.get_by_role(role.strip(), **options)
            return self.page.get_by_role(role_part.strip())
            
        elif selector.startswith("text:"):
            return self.page.get_by_text(selector[5:])
            
        elif selector.startswith("label:"):
            return self.page.get_by_label(selector[6:])
            
        elif selector.startswith("placeholder:"):
            return self.page.get_by_placeholder(selector[12:])
            
        elif selector.startswith("testid:"):
            return self.page.get_by_test_id(selector[7:])
            
        elif selector.startswith("xpath:"):
            return self.page.locator(selector[6:])
            
        elif selector.startswith("css:"):
            return self.page.locator(selector[4:])
            
        else:
            # Default to CSS/auto-detect
            return self.page.locator(selector)


async def run_test_steps(runner: E2ETestRunner, steps: list[dict]) -> dict:
    """
    Execute a sequence of test steps.
    
    Args:
        runner: E2ETestRunner instance
        steps: List of step dictionaries with action and params
        
    Returns:
        Results dict with success status and any captured data
    """
    results = {"success": True, "steps": [], "error": None}
    
    for i, step in enumerate(steps):
        action = step.get("action")
        params = step.get("params", {})
        step_name = step.get("name", f"Step {i + 1}")
        
        try:
            if action == "navigate":
                await runner.navigate(params["url"])
            elif action == "click":
                await runner.click(params["selector"], **params.get("options", {}))
            elif action == "fill":
                await runner.fill(params["selector"], params["value"])
            elif action == "type":
                await runner.type_text(
                    params["selector"], params["text"], params.get("delay", 50)
                )
            elif action == "select":
                await runner.select_option(params["selector"], params["value"])
            elif action == "check":
                await runner.check(params["selector"])
            elif action == "uncheck":
                await runner.uncheck(params["selector"])
            elif action == "hover":
                await runner.hover(params["selector"])
            elif action == "wait":
                await runner.wait_for(params["selector"], params.get("state", "visible"))
            elif action == "screenshot":
                path = await runner.screenshot(
                    params.get("name", step_name),
                    full_page=params.get("full_page", False),
                    selector=params.get("selector"),
                )
                results["steps"].append({
                    "name": step_name,
                    "action": action,
                    "screenshot_path": str(path),
                })
                continue
            elif action == "pause":
                await asyncio.sleep(params.get("seconds", 1))
            else:
                raise ValueError(f"Unknown action: {action}")
                
            results["steps"].append({"name": step_name, "action": action, "success": True})
            
        except Exception as e:
            results["success"] = False
            results["error"] = f"{step_name}: {str(e)}"
            results["steps"].append({
                "name": step_name,
                "action": action,
                "success": False,
                "error": str(e),
            })
            # Take failure screenshot
            await runner.screenshot(f"FAILURE_{step_name}")
            break
            
    return results


async def main():
    parser = argparse.ArgumentParser(description="Run E2E feature tests with Playwright")
    parser.add_argument("--url", required=True, help="Starting URL for the test")
    parser.add_argument("--steps", help="JSON file with test steps")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--background", action="store_true", help="Run browser off-screen (no focus stealing)")
    parser.add_argument("--screenshot-dir", default="/tmp/e2e_screenshots")
    parser.add_argument("--timeout", type=int, default=30000, help="Default timeout in ms")
    parser.add_argument("--width", type=int, default=1280, help="Viewport width")
    parser.add_argument("--height", type=int, default=720, help="Viewport height")
    
    args = parser.parse_args()
    
    runner = E2ETestRunner(
        headless=args.headless,
        screenshot_dir=args.screenshot_dir,
        timeout=args.timeout,
        viewport_width=args.width,
        viewport_height=args.height,
        background=args.background,
    )
    
    try:
        await runner.setup()
        
        # If steps file provided, run those steps
        if args.steps:
            with open(args.steps) as f:
                steps = json.load(f)
            results = await run_test_steps(runner, steps)
        else:
            # Simple navigation and screenshot
            await runner.navigate(args.url)
            await runner.screenshot("initial_page")
            results = {"success": True, "message": "Page loaded successfully"}
            
        # Output results as JSON
        print(json.dumps(results, indent=2))
        
        # Get screenshots for analysis
        screenshots = runner.get_screenshots_for_analysis()
        if screenshots:
            print(f"\nCaptured {len(screenshots)} screenshot(s) for analysis.")
            for s in screenshots:
                print(f"  - {s['name']}: {s['path']}")
                
    finally:
        await runner.teardown()


if __name__ == "__main__":
    asyncio.run(main())
