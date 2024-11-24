import textwrap
from colorama import Fore, Style
from example_runner import ExampleRunner

from utils import paginate_output

class SiteScraper:
    """_summary_
        Represents an example of configuring and calling a SiteScraper using Nexus.

    """
    def __init__(
        self,
        client,
        package_id,
        model_id,
        model_owner_cap_id,
        url,
    ):
        """
        Create a SiteScraper object.

        Parameters
        ----------
        client : pysui.sui.sui_client.SuiClient
            The Sui client to use.
        package_id : ObjectID
            The ID of the package containing the "cluster" module.
        model_id : ObjectID
            The ID of the model.
        model_owner_cap_id : ObjectID
            The ID of the capability that owns the model.
        url : str
            The URL to be summarized.
        """
        self.example_runner = ExampleRunner(client, package_id, model_id, model_owner_cap_id)
        self.url = url

    def setup_agents(self):
        # Create agents (assuming we have model_ids and model_owner_cap_ids)
        self.example_runner.add_agent(
                "site_scraper",
                "Site Scraping Agent",
                "Scrape the selected website and summarize its content",
            ),

    def setup_tasks(self):
        self.example_runner.add_task(
            task_name="scrape_site",
            agent_name="site_scraper",
            description=f"Scrape and summarize the following site: {self.url}")

    def setup_tools(self):
        self.example_runner.add_tool(
            task_name="scrape_site",
            tool_name="browser",
            tool_args=[
                f"""
                    url: {self.url}
                """,
                ]
            )

    def run(self):
        self.setup_agents()
        self.setup_tasks()
        self.setup_tools()
        return self.example_runner.execute()


        # return self.example_runner.execute(
        #     user_input=
        #     f"""
        #         Execute the task site_scraper: Url: {self.url}
        #     """,
        # )


def run_site_summary_example(client, package_id, model_id, mode_owner_cap):
    print(f"{Fore.CYAN}## Welcome to Site Scraper using Nexus{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}-------------------------------{Style.RESET_ALL}")

    url = input(f"{Fore.GREEN}What is the URL to be summarized? {Style.RESET_ALL}")

    scraper = SiteScraper(
        client,
        package_id,
        model_id,
        mode_owner_cap,
        url
    )

    print()
    result = scraper.run()

    print(f"\n\n{Fore.CYAN}########################{Style.RESET_ALL}")
    print(f"{Fore.CYAN}## Results {Style.RESET_ALL}")
    print(f"{Fore.CYAN}########################\n{Style.RESET_ALL}")

    paginate_output(result)

