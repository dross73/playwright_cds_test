import tkinter as tk  # Main GUI toolkit
from typing import Dict, List
from tkinter import messagebox  # for popup error messages


# This function creates the GUI, collects user input, and returns it as a dictionary
def get_user_input() -> Dict[str, List[str]]:
    # This nested function is triggered when the user clicks the "Run Tests" button
    def submit() -> None:
        # Get the full text from the multi-line Text widget
        url_input = text_box.get("1.0", tk.END)  # First char until the end

        # Split the text into lines, strip whitespace, and ignore empty lines
        urls = [url.strip() for url in url_input.strip().splitlines() if url.strip()]

        # Validate: make sure at least one URL was entered.
        if not urls:
            messagebox.showerror("Error", "Please enter at least one URL")
            return

        # Get the selected region from the dropdown (e.g., "US")
        # region = region_var.get()

        # Get the selected indices from the payment type listbox
        selected_indices = pay_listbox.curselection()

        # Convert selected indices into actual strings (e.g., "PayPal")
        pay_types = [pay_options[i] for i in selected_indices]

        # Validate: make sure at least one payment type was selected
        if not pay_types:
            messagebox.showerror("Error", "Please select at least one payment type.")
            return

        # Store all collected data in a dictionary
        input_data["urls"] = urls
        # input_data["region"] = region
        input_data["pay_types"] = pay_types

        # Close the GUI window
        root.destroy()

    # This dictionary will hold all the user input and get returned at the end.
    input_data = {}

    # Create the main GUI window
    root = tk.Tk()
    root.title("QC Test Input")  # Set the window title

    # Label above the text box
    tk.Label(root, text="Enter one URL per line:").pack(padx=10, pady=(10, 0))

    # Multi-line text box for URL input
    text_box = tk.Text(root, height=10, width=70)
    text_box.pack(padx=10, pady=(0, 10))

    # Dropdown for region selection
    # tk.Label(root, text="Select Region:").pack()
    # region_var = tk.StringVar(value="US") # Default value is "US"
    # region_dropdown = tk.OptionMenu(root, region_var, "US", "CAN", "INTL", "ALL")
    # region_dropdown.pack(pady=(0, 10))

    # Label for payment types
    tk.Label(root, text="Select Payment Types to Test:").pack()

    # Multi-select listbox for payment types
    pay_options = ["Credit Card", "PayPal", "Amazon"]
    pay_listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, height=len(pay_options))
    for option in pay_options:
        pay_listbox.insert(tk.END, option)
    pay_listbox.pack(padx=10, pady=(0, 10))

    # Submit button to trigger the test
    tk.Button(root, text="Run Tests", command=submit).pack(pady=(0, 15))

    # Start the GUI event loop - waits for user interaction
    root.mainloop()

    # Return the dictionary of user inputs to the caller
    return input_data
