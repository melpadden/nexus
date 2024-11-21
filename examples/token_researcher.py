# Use [run_token_researcher_example] to run the example.
# It's atakes a ctoken symbol as argument
# and then gives the user details about the token's characteristics

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

class TokenResearcher:
    def __init__(
        self,
        client,
        package_id,
        model_id,
        model_owner_cap_id,
        token_symbol
    ):
        self.client = client
        self.package_id = package_id
        self.model_id = model_id
        self.model_owner_cap_id = model_owner_cap_id

        self.token_symbol = token_symbol

    def setup_cluster(self):
        # Create a cluster (equivalent to Crew in CrewAI)
        cluster_id, cluster_owner_cap_id = create_cluster(
            self.client,
            self.package_id,
            "Token Researching Cluster",
            "A cluster for figuring out the best way to use tokens",
        )
        return cluster_id, cluster_owner_cap_id

    def setup_agents(self, cluster_id, cluster_owner_cap_id):
        # Create agents (assuming we have model_ids and model_owner_cap_ids)
        agent_configs = [
            (
                "token_stats",
                "Token Statistics Agent",
                "Analyze and select the statistics for the token to be researched. Retrieve the statistics from https://tokenterminal.com/explorer.",
            ),
            (
                "token_info",
                "Token Info Agent",
                "Retrieve general information about the token.",
            ),
            (
                "token_risks",
                "Token Risks Agent",
                "Analyse if any potential risks exist for this token to devalue in the next 6 months.",
            ),
            (
                "token_upside",
                "Token Upside Agent",
                "Analyse if any potential risks exist for this token to devalue in the next 6 months.",
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
                f"An AI agent specialized in {role.lower()} for token research.",
            )

    def setup_tasks(self, cluster_id, cluster_owner_cap_id):
        tasks = [
            (
                "get_statistics", # task name
                "token_stats", # agent id
                f"""
                Analyze and select the statistics for the token to be researched. Retrieve the statistics from https://tokenterminal.com/explorer.
                Token: {self.token_symbol}
            """,
            ),
            (
                "gather_info",
                "token_info",
                f"""
                Retrieve general information about the token.
                Token: {self.token_symbol}
            """,
            ),
            (
                "get_risks",
                "token_risks",
                f"""
                Analyse if any potential risks exist for this token to devalue in the next 6 months.
                Token: {self.token_symbol}
            """,
            ),
            (
                "get_upside",
                "token_upside",
                f"""
                Analyse if there are any potential positive developments for this token in the next 6 months.
                Token: {self.token_symbol}
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
                f"Complete {task_name} for token research",
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
            Get research about this token: {self.token_symbol}.
        """,
        )

        if execution_id is None:
            return "Cluster execution failed"

        print(f"Cluster execution started with ID: {execution_id}")
        return get_cluster_execution_response(self.client, execution_id, 600)


# Runs the Trip Planner example using the provided Nexus package ID.
def run_token_researcher_example(client, package_id, model_id, mode_owner_cap):
    print(f"{Fore.CYAN}## Welcome to Token  Planner using Nexus{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}-------------------------------{Style.RESET_ALL}")

    token = input(f"{Fore.GREEN}Which token would you like to research? {Style.RESET_ALL}")

    researcher = TokenResearcher(
        client,
        package_id,
        model_id,
        mode_owner_cap,
        token,
    )

    print()
    result = researcher.run()

    print(f"\n\n{Fore.CYAN}########################{Style.RESET_ALL}")
    print(f"{Fore.CYAN}## Here is your Token Research {Style.RESET_ALL}")
    print(f"{Fore.CYAN}########################\n{Style.RESET_ALL}")

    paginate_output(result)
