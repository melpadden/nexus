import textwrap
from colorama import Fore, Style

# Helper function to paginate the result output
def paginate_output(text, width=80):
    lines = text.split("\n")

    for i, line in enumerate(lines, 1):
        wrapped_line = textwrap.fill(line, width)
        print(wrapped_line)

        # It's nice when this equals the number of lines in the terminal, using
        # default value 32 for now.
        pause_every_n_lines = 32
        if i % pause_every_n_lines == 0:
            input(f"{Fore.YELLOW}-- Press Enter to continue --{Style.RESET_ALL}")
