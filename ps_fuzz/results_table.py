import colorama
from prettytable import PrettyTable, SINGLE_BORDER

RESET = colorama.Style.RESET_ALL
BRIGHT = colorama.Style.BRIGHT
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
BRIGHT_YELLOW = colorama.Fore.LIGHTYELLOW_EX + colorama.Style.BRIGHT

def print_table(title, headers, data, footer_row=None):
    print(f"{BRIGHT}{title}{RESET} ...")
    table = PrettyTable(
        align="l",
        field_names = [f"{BRIGHT}{h}{RESET}" for h in headers]
    )
    table.set_style(SINGLE_BORDER)
    for data_row in data:
        table_row = []
        for i, _ in enumerate(headers):
            table_row.append(f"{data_row[i]}")
        table.add_row(table_row)
    if (footer_row):
        table.add_row(footer_row)

    # Trick below simulates a footer line separated from the header and body by a separator line
    table_lines = table.get_string().split("\n")
    if footer_row:
        # Extract the header-body separator line (second line) and put it sabove the last (footer) row
        table_lines = table_lines[:-2] + [table_lines[2]] + table_lines[-2:]


    for table_line in table_lines:
        print(table_line)

if __name__ == "__main__":
    PASSED = f"{GREEN}✔{RESET}"
    FAILED = f"{RED}✘{RESET}"
    ERROR = f"{BRIGHT_YELLOW}⚠{RESET}"

    print_table(
        title = "Test results simulated",
        headers = ["", "Test", "Succesful", "Unsuccesful", "Score (1-10)"],
        data = [
            [ PASSED, "Test 1 (good)", 1, 0, 10 ],
            [ FAILED, "Test 2 (bad)", 0, 1, 0 ],
            [ ERROR, "Test 3 (with errors)", 5, 0, 5 ],
        ]
    )

    print_table(
        title = "Test results simulated with footer",
        headers = ["", "Test", "Succesful", "Unsuccesful", "Score (1-10)"],
        data = [
            [ PASSED, "Test 1 (good)", 1, 0, 10 ],
            [ FAILED, "Test 2 (bad)", 0, 1, 0 ],
            [ ERROR, "Test 3 (with errors)", 5, 0, 5 ],
        ],
        footer_row=[FAILED, "Total", 6, 1, 5.5]
    )
