import textwrap
from colorama import Fore, Style
from utils import paginate_output
from nexus_sdk import (
    create_cluster,
    create_agent_for_cluster,
    create_task,
    execute_cluster,
    get_cluster_execution_response,
)

from pysui.sui.sui_txn.sync_transaction import SuiTransaction
from pysui.sui.sui_types.scalars import ObjectID, SuiString
from pysui.sui.sui_types.collections import SuiArray

class SiteScraper:
    def __init__(
        self,
        client,
        package_id,
        model_id,
        model_owner_cap_id,
        url,
    ):
        self.client = client
        self.package_id = package_id
        self.model_id = model_id
        self.model_owner_cap_id = model_owner_cap_id

        self.url = url

    def setup_cluster(self):
        # Create a cluster (equivalent to Crew in CrewAI)
        cluster_id, cluster_owner_cap_id = create_cluster(
            self.client,
            self.package_id,
            "Site Scraping Cluster",
            "A cluster for scraping websites",
        )
        return cluster_id, cluster_owner_cap_id

    def setup_agents(self, cluster_id, cluster_owner_cap_id):
        # Create agents (assuming we have model_ids and model_owner_cap_ids)
        agent_configs = [
            (
                "site_scraper",
                "Site Scraping Agent",
                "Scrape the selected website and summarize its content",
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
                "scrape_site",
                "site_scraper",
                f"""
                Scrape and summarize the following site: {self.url}
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
                f"Complete {task_name} ",
                description,
                "",  # No specific context provided in this example
            )
            task_ids.append(task_id)

        return task_ids


    def setup_tools(self, cluster_id, cluster_owner_cap_id):
        tools = [
            (
                "scrape_site",  # task_name
                "browser", # tool_name
                # tool_args
                f"""
                url: {self.url}
            """,
            ),

        ]
        for task_name, tool_name, tool_args in tools:
            self.attach_tool_to_task(
                cluster_id=cluster_id,
                cluster_owner_cap_id=cluster_owner_cap_id,
                task_name=task_name,
                tool_name=tool_name,
                tool_args=tool_args,
            )

    def attach_tool_to_task(
        self,
        cluster_id,
        cluster_owner_cap_id,
        task_name,
        tool_name,
        tool_args,
    ):
        txn = SuiTransaction(client=self.client)

        try:
            result = txn.move_call(
                target=f"{self.package_id}::cluster::attach_tool_to_task_entry",
                arguments=[
                    ObjectID(cluster_id),
                    ObjectID(cluster_owner_cap_id),
                    SuiString(task_name),
                    SuiString(tool_name),
                    SuiArray([SuiString(arg) for arg in tool_args]),
                ],
            )
        except Exception as e:
            print(f"Error in attach_task_to_tool: {e}")
            return None

        result = txn.execute(gas_budget=10000000)

        if result.is_ok():
            if result.result_data.effects.status.status == "success":
                print(f"Task attached to Tool")
                return True
            else:
                error_message = result.result_data.effects.status.error
                print(f"Transaction failed: {error_message}")
                return None
        return None

    def run(self):
        cluster_id, cluster_owner_cap_id = self.setup_cluster()
        self.setup_agents(cluster_id, cluster_owner_cap_id)
        self.setup_tasks(cluster_id, cluster_owner_cap_id)
        self.setup_tools(cluster_id, cluster_owner_cap_id)

        execution_id = execute_cluster(
            self.client,
            self.package_id,
            cluster_id,
            f"""
            Site Scraper: Url: {self.url}
        """,
        )

        if execution_id is None:
            return "Cluster execution failed"

        print(f"Cluster execution started with ID: {execution_id}")
        return get_cluster_execution_response(self.client, execution_id, 600)


def run_site_summary_example(client, package_id, model_id, mode_owner_cap):
    print(f"{Fore.CYAN}## Welcome to Site Scraper using Nexus{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}-------------------------------{Style.RESET_ALL}")

    url = input(f"{Fore.GREEN}What is the URL to be summarized? {Style.RESET_ALL}")

    runner = SiteScraper(
        client,
        package_id,
        model_id,
        mode_owner_cap,
        url
    )

    print()
    result = runner.run()

    print(f"\n\n{Fore.CYAN}########################{Style.RESET_ALL}")
    print(f"{Fore.CYAN}## Results {Style.RESET_ALL}")
    print(f"{Fore.CYAN}########################\n{Style.RESET_ALL}")

    paginate_output(result)

