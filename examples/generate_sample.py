"""Generate examples/sample.xlsx — synthetic Azure DevOps-style export.

Run:
    python examples/generate_sample.py
"""
from pathlib import Path
from openpyxl import Workbook

OUT = Path(__file__).parent / "sample.xlsx"

HEADERS = ["ID", "Work Item Type", "Title", "Test Step",
           "Step Action", "Step Expected", "Area Path", "Assigned To", "State"]

# Synthetic test cases: a fictional web app login + form flow.
DATA = [
    # --- Test Case 1: Login success ---
    [101, "Test Case", "Login - Successful sign-in with valid credentials",
     None, None, None, "WebApp\\Auth", "alice@example.com", "Design"],
    [None, None, None, "1", "Open the application URL", "Login page is displayed", None, None, None],
    [None, None, None, "2", "Type a valid username in the Email field",
     "Field accepts the value", None, None, None],
    [None, None, None, "3", "Type a valid password in the Password field",
     "Characters are masked", None, None, None],
    [None, None, None, "4", "Click the Sign In button",
     "User is redirected to the dashboard", None, None, None],

    # --- Test Case 2: Login failure ---
    [102, "Test Case", "Login - Failure with invalid password",
     None, None, None, "WebApp\\Auth", "alice@example.com", "Design"],
    [None, None, None, "1", "Open the application URL", "Login page is displayed", None, None, None],
    [None, None, None, "2", "Type a valid username", "Field accepts the value", None, None, None],
    [None, None, None, "3", "Type an invalid password", "Characters are masked", None, None, None],
    [None, None, None, "4", "Click the Sign In button",
     "Error message 'Invalid credentials' is displayed", None, None, None],
    [None, None, None, "5", "Verify the user remains on the login page",
     "URL has not changed", None, None, None],

    # --- Test Case 3: Form validation ---
    [103, "Test Case", "Profile form - Required field validation",
     None, None, None, "WebApp\\Profile", "bob@example.com", "Design"],
    [None, None, None, "1", "Sign in as a regular user", "Dashboard is shown", None, None, None],
    [None, None, None, "2", "Navigate to Profile > Edit", "Profile form is displayed", None, None, None],
    [None, None, None, "3", "Clear the Full Name field and click Save",
     "Form shows validation error 'Full name is required'", None, None, None],
    [None, None, None, "4", "Fill in Full Name and click Save",
     "Profile is saved and a success toast appears", None, None, None],
]


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    ws.append(HEADERS)
    for row in DATA:
        ws.append(row)
    wb.save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
