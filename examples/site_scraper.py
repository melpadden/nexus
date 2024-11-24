import textwrap
from colorama import Fore, Style
import utils
import nexus_sdk as nexus_sdk
#from nexus_sdk import cluster

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
        self.tools = []

        self.url = url

    def setup_cluster(self):
        # Create a cluster (equivalent to Crew in CrewAI)
        cluster_id, cluster_owner_cap_id = nexus_sdk.create_cluster(
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
            nexus_sdk.create_agent_for_cluster(
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
            task_id = nexus_sdk.create_task(
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

        # tools = [
        #     (
        #         "scrape_site",  # task_name
        #         "browser", # tool_name
        #         # tool_args
        #         f"""
        #         url: {self.url}
        #     """,
        #     ),
        # ]
        self.tools = [
            (
                "scrape_site",  # task_name
                "browser", # tool_name
                [self.url]
            ),
        ]

        for task_name, tool_name, tool_args in self.tools:
            nexus_sdk.attach_tool_to_task(
                client=self.client,
                package_id=self.package_id,
                cluster_id=cluster_id,
                cluster_owner_cap_id=cluster_owner_cap_id,
                task_name=task_name,
                tool_name=tool_name,
                tool_args=tool_args,
            )



    def run(self):
        # cluster_id, cluster_owner_cap_id = self.setup_cluster()
        # self.setup_agents(cluster_id, cluster_owner_cap_id)
        # self.setup_tasks(cluster_id, cluster_owner_cap_id)
        # self.setup_tools(cluster_id, cluster_owner_cap_id)

        print(f"{self.url}")
        print(f"Setting up cluster..")

        cluster_id, cluster_owner_cap_id = self.setup_cluster()
        print(f"cluster_id, cluster_owner_cap_id : {cluster_id, cluster_owner_cap_id }")
        print(f"Setting up agents..")
        self.setup_agents(cluster_id, cluster_owner_cap_id)
        print(f"Setting up tasks..")
        self.setup_tasks(cluster_id, cluster_owner_cap_id)
        print(f"Setting up tools..")
        self.setup_tools(cluster_id, cluster_owner_cap_id)

        print(f"Successfully set up tools. Attached {len(self.tools)} tools..")
        for tool in self.tools:
            print(f"{tool}")

        print(f"Starting cluster execution..")
        execution_id = nexus_sdk.execute_cluster(
            self.client,
            self.package_id,
            cluster_id,
            f"""
                Site Scraper: Url: {self.url}
            """,
        )

        if execution_id is None:
            return "Start Cluster execution failed"

        print(f"Cluster execution started with ID: {execution_id}")
        return nexus_sdk.get_cluster_execution_response(self.client, execution_id, 600)


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

    result = runner.run()

    print(f"\n\n{Fore.CYAN}########################{Style.RESET_ALL}")
    print(f"{Fore.CYAN}## Results {Style.RESET_ALL}")
    print(f"{Fore.CYAN}########################\n{Style.RESET_ALL}")

    utils.paginate_output(result)

