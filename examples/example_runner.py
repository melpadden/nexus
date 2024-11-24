import nexus_sdk as nexus
from pysui.sui.sui_txn.sync_transaction import SuiTransaction
from pysui.sui.sui_types.scalars import ObjectID, SuiString
from pysui.sui.sui_types.collections import SuiArray


class ExampleRunner:
    """_summary_
        Encapsulates some resusable logic for running examples.
        Basically a dupe of the logic in cli_cluster.py with some additions
        In a classic OO language this would probably be a base class but I prefer compositional patterns in Python
    """
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

        """
        Create an ExampleRunner object.

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
        agents : list[dict]
            A list of dictionaries, each containing the "name", "role", and "goal" of an agent.
        tasks : list[dict]
            A list of dictionaries, each containing the "name", "agent", "description", "expected_output", "prompt", and "context" of a task.
        tools : list[dict]
            A list of dictionaries, each containing the "name", "description", "expected_output", "prompt", and "context" of a tool.
        """
        self.client = client
        self.package_id = package_id
        self.model_id = model_id
        self.model_owner_cap_id = model_owner_cap_id

        self.agent_configs = agents
        self.task_configs = tasks
        self.tool_configs = tools

    def add_agent(self, agent_name, role, goal):
        agt = [agt for agt in self.agent_configs if agt[0] == agent_name]
        if agt:
            raise Exception(f"Agent {agent_name} is already configured: attempt to configure duplicate agent.")

        self.agent_configs.append((agent_name, role, goal))

    def add_task(self, task_name, agent_name, description):
        agent_present = [ag for ag in self.agent_configs if ag[0] == agent_name]
        task_present = [t for t in self.task_configs if t[0] == task_name]
        print(f"{agent_present} {task_present} ")
        if task_present:
            raise Exception(f"Task {task_name} is already present: attempt to add duplicate task.")
        if not agent_present:
            raise Exception(f"Agent {agent_name} is not configured: attempt to add orphan task")

        self.task_configs.append((task_name, agent_name, description))

    def add_tool(self, task_name, tool_name, tool_args):
        task_present = [tsk for tsk in self.task_configs if tsk[0] == task_name]
        tool_present = [tl for tl in self.tool_configs if tl[0] == tool_name]
        if tool_present:
            raise Exception(f"Tool {tool_name} is already configured: Attempt to add duplicate tool")
        if not task_present:
            raise Exception(f"Task {task_name} is not configured: attempt to add orphan tool")

        self.tool_configs.append((task_name, tool_name, tool_args))

    def init_cluster(self):
        # Create a cluster (equivalent to Crew in CrewAI)
        cluster_id, cluster_owner_cap_id = nexus.create_cluster(
            self.client,
            self.package_id,
            "Example Cluster",
            "A cluster for running example Nexus agents",
        )
        return cluster_id, cluster_owner_cap_id

    def init_agents(self, cluster_id, cluster_owner_cap_id):

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

    def init_tasks(self, cluster_id, cluster_owner_cap_id):
        """
        Create all tasks that have been configured using add_task.

        Tasks are created on the given cluster and with the given agent.

        Args:
            cluster_id (str): The ID of the cluster to which the task belongs
            cluster_owner_cap_id (str): The ID of the capability that owns the cluster

        Returns:
            list[str]: A list of the IDs of the tasks created
        """
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


    def init_tools(self, cluster_id, cluster_owner_cap_id):
        """
        Attach all tools that have been configured using add_tool to their associated tasks.

        Tools are attached to tasks on the given cluster and with the given agent.

        Args:
            cluster_id (str): The ID of the cluster to which the task belongs
            cluster_owner_cap_id (str): The ID of the capability that owns the cluster
        """
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
        """
        Attaches a tool to a task in the given cluster.

        Args:
            client: The Sui client to use
            package_id: The ID of the package containing the "cluster" module
            cluster_id: The ID of the cluster to which the agent should be added
            cluster_owner_cap_id: The ID of the capability that owns the cluster
            task_name: The name of the task
            tool_name: The name of the tool
            tool_args: The arguments to the tool

        Returns:
            True if the tool was successfully attached to the task, False otherwise
        """
        # TODO: This should be moved into the SDK, it belongs with the other SUI-dependent functions.
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

    def execute(self, user_input=[]):
        """
        Execute the cluster with the given user input.

        This function sets up the cluster, agents, tasks, and tools, and then executes the cluster with the given user input.

        Args:
            user_input: The user input to pass to the cluster

        Returns:
            The result of the cluster execution, or "Cluster execution failed" if it failed
        """
        cluster_id, cluster_owner_cap_id = self.init_cluster()
        self.init_agents(cluster_id, cluster_owner_cap_id)
        self.init_tasks(cluster_id, cluster_owner_cap_id)
        self.init_tools(cluster_id, cluster_owner_cap_id)

        execution_id = nexus.execute_cluster(
            self.client,
            self.package_id,
            cluster_id,
            user_input)

        if execution_id is None:
            raise Exception("Cluster execution failed")

        print(f"Cluster execution started with ID: {execution_id}")
        # this is a blocking call which waits for the execution to complete
        return nexus.get_cluster_execution_response(self.client, execution_id, 600)

