import nexus_sdk as nexus
from pysui.sui.sui_txn.sync_transaction import SuiTransaction
from pysui.sui.sui_types.scalars import ObjectID, SuiString
from pysui.sui.sui_types.collections import SuiArray


class ExampleRunner:
    def __init__(
        self,
        client,
        package_id,
        model_id,
        model_owner_cap_id,
        agents = [],
        tasks = [],
        tools = [],
    ):
        self.client = client
        self.package_id = package_id
        self.model_id = model_id
        self.model_owner_cap_id = model_owner_cap_id

        self.agent_configs = agents
        self.task_configs = tasks
        self.tool_configs = tools

    def add_agent(self, agent_name, role, goal):
        self.agent_configs.append((agent_name, role, goal))
    def add_task(self, task_name, agent_id, description):
        self.task_configs.append((task_name, agent_id, description))
    def add_tool(self, task_name, tool_name, tool_args):
        self.tool_configs.append((task_name, tool_name, tool_args))

    def setup_cluster(self):
        # Create a cluster (equivalent to Crew in CrewAI)
        cluster_id, cluster_owner_cap_id = nexus.create_cluster(
            self.client,
            self.package_id,
            "Example Cluster",
            "A cluster for running example Nexus agents",
        )
        return cluster_id, cluster_owner_cap_id

    def setup_agents(self, cluster_id, cluster_owner_cap_id):

        for agent_name, role, goal in self.agent_configs:
            nexus.create_agent_for_cluster(
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

        task_ids = []
        for task_name, agent_id, description in self.task_configs:
            task_id = nexus.create_task(
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
        for task_name, tool_name, tool_args in self.tool_configs:
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

    def execute(self, user_input):
        cluster_id, cluster_owner_cap_id = self.setup_cluster()
        self.setup_agents(cluster_id, cluster_owner_cap_id)
        self.setup_tasks(cluster_id, cluster_owner_cap_id)
        self.setup_tools(cluster_id, cluster_owner_cap_id)

        execution_id = nexus.execute_cluster(
            self.client,
            self.package_id,
            cluster_id,
            user_input)

        if execution_id is None:
            return "Cluster execution failed"

        print(f"Cluster execution started with ID: {execution_id}")
        return nexus.get_cluster_execution_response(self.client, execution_id, 600)

