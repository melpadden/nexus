import textwrap
from colorama import Fore, Style
from example_runner import ExampleRunner
from utils import paginate_output

class PromptRunner:
    def __init__(
        self,
        client,
        package_id,
        model_id,
        model_owner_cap_id,
        instructions
    ):
        self.example_runner = ExampleRunner(client, package_id, model_id, model_owner_cap_id)
        self.instructions = instructions

    def setup_agents(self):
        self.example_runner.add_agent(agent_name="prompt_agent", role="Prompt Agent", goal="Process a prompt")

    def setup_tasks(self):
        self.example_runner.add_task( task_name="prompt_task", agent_name="prompt_agent", description=self.instructions)

    def setup_tools(self):
        self.example_runner.add_tool(
            task_name="prompt_task",
            tool_name="prompt",
            tool_args=[
                f"""
                    prompt: {self.instructions}
                """,
                ]
            )
    def run(self):
        self.setup_agents()
        self.setup_tasks()
        self.setup_tools()

        return self.example_runner.execute()
        # return self.example_runner.execute(input=self.instructions)


# Runs the Task Runner example using the provided Nexus package ID.
def run_prompt_task_example(client, package_id, model_id, mode_owner_cap):
    print(f"{Fore.CYAN}## Welcome to Prompt Example using Nexus{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}-------------------------------{Style.RESET_ALL}")

    instructions = input(f"{Fore.GREEN}Enter the prompt for the task {Style.RESET_ALL}")

    runner = PromptRunner(
        client,
        package_id,
        model_id,
        mode_owner_cap,
        instructions
    )

    print()
    result = runner.run()

    print(f"\n\n{Fore.CYAN}########################{Style.RESET_ALL}")
    print(f"{Fore.CYAN}## Here is your output {Style.RESET_ALL}")
    print(f"{Fore.CYAN}########################\n{Style.RESET_ALL}")

    paginate_output(result)
