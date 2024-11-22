# Use [run_task] to run the example.
# It runs the simplest possible task that can be executed
# and then prints the output

import textwrap
from colorama import Fore, Style
from nexus_sdk import (
    create_cluster,
    create_agent_for_cluster,
    create_task,
    execute_cluster,
    get_cluster_execution_response,
)
from utils import paginate_output

class TaskRunner:
    def __init__(
        self,
        client,
        package_id,
        model_id,
        model_owner_cap_id,
        task_name,
        purpose,
        instructions
    ):
        self.client = client
        self.package_id = package_id
        self.model_id = model_id
        self.model_owner_cap_id = model_owner_cap_id

        self.purpose = purpose
        self.instructions = instructions
        self.task_name = task_name

    def setup_cluster(self):
        # Create a cluster (equivalent to Crew in CrewAI)
        cluster_id, cluster_owner_cap_id = create_cluster(
            self.client,
            self.package_id,
            "Task Running Cluster",
            "A cluster for Running a simple task",
        )
        return cluster_id, cluster_owner_cap_id

    def setup_agents(self, cluster_id, cluster_owner_cap_id):
        # Create agents (assuming we have model_ids and model_owner_cap_ids)
        agent_configs = [
            (
                "task_runner",
                "Task Runner",
                self.purpose,
            ),
        ]

        for agent_name, role, goal in agent_configs:
            create_agent_for_cluster(
                self.client,
                self.package_id,
                cluster_id,
                cluster_owner_cap_id,
                self.model_id,
                self.model_owner_cap_id,
                agent_name,
                role,
                goal,
                f"An AI agent specialized in {role.lower()}.",
            )

    def setup_tasks(self, cluster_id, cluster_owner_cap_id):
        tasks = [
            (
                "task_name", # task name
                "task_runner", # agent id
                f"""
                {self.instructions}
            """,
            ),
        ]

        task_ids = []
        for task_name, agent_id, description in tasks:
            task_id = create_task(
                self.client,
                self.package_id,
                cluster_id,
                cluster_owner_cap_id,
                task_name,
                agent_id,
                description,
                f"Complete {task_name} task.",
                description,
                "",  # No specific context provided in this example
            )
            task_ids.append(task_id)

        return task_ids

    def run(self):
        cluster_id, cluster_owner_cap_id = self.setup_cluster()
        self.setup_agents(cluster_id, cluster_owner_cap_id)
        self.setup_tasks(cluster_id, cluster_owner_cap_id)

        execution_id = execute_cluster(
            self.client,
            self.package_id,
            cluster_id,
            f"""
            Execute this task: {self.task_name}.
        """,
        )

        if execution_id is None:
            return "Cluster execution failed"

        print(f"Cluster execution started with ID: {execution_id}")
        return get_cluster_execution_response(self.client, execution_id, 600)


# Runs the Task Runner example using the provided Nexus package ID.
def run_prompt_task_example(client, package_id, model_id, mode_owner_cap):
    print(f"{Fore.CYAN}## Welcome to Task Runner using Nexus{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}-------------------------------{Style.RESET_ALL}")

    task_name = input(f"{Fore.GREEN}Enter a short name for the task {Style.RESET_ALL}")
    purpose = input(f"{Fore.GREEN}Enter a purpose for the task {Style.RESET_ALL}")
    instructions = input(f"{Fore.GREEN}Enter the instructions for the task {Style.RESET_ALL}")

    runner = TaskRunner(
        client,
        package_id,
        model_id,
        mode_owner_cap,
        task_name,
        purpose,
        instructions
    )

    print()
    result = runner.run()

    print(f"\n\n{Fore.CYAN}########################{Style.RESET_ALL}")
    print(f"{Fore.CYAN}## Here is your output {Style.RESET_ALL}")
    print(f"{Fore.CYAN}########################\n{Style.RESET_ALL}")

    paginate_output(result)
