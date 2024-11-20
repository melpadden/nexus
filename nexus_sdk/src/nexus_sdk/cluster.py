from pysui.sui.sui_builders.get_builders import GetObject
from pysui.sui.sui_txn.sync_transaction import SuiTransaction
from pysui.sui.sui_types.scalars import ObjectID, SuiString
import time
import ast
import traceback

# Equal to 1 SUI which should be enough for most transactions.
GAS_BUDGET = 1000000000


def create_cluster(client, package_id, name, description, gas_budget=GAS_BUDGET):
    """
    Creates an empty cluster object to which agents and tasks can be added.
    See functions [create_agent_for_cluster] and [create_task].

    Args:
        client: The Sui client to use
        package_id: The ID of the package containing the "cluster" module
        name: The name of the cluster
        description: A description of the cluster
        gas_budget: The gas budget for the transaction (default = 1 SUI)

    Returns:
        A tuple containing the cluster ID and the cluster owner capability ID, or None if the
        transaction failed.
    """
    txn = SuiTransaction(client=client)

    try:
        result = txn.move_call(
            target=f"{package_id}::cluster::create",
            arguments=[SuiString(name), SuiString(description)],
        )
        result = txn.execute(gas_budget=gas_budget)
        if result.is_ok():
            if result.result_data.effects.status.status == "success":
                # just because it says "parsed_json" doesn't mean it's actually valid JSON apparently
                not_json = result.result_data.events[0].parsed_json
                created_event = ast.literal_eval(not_json.replace("\n", "\\n"))
                cluster_id = created_event["cluster"]
                cluster_owner_cap_id = created_event["owner_cap"]

                return cluster_id, cluster_owner_cap_id
        print(f"Failed to create Cluster: {result.result_string}")
        return None
    except Exception as e:
        print(f"Error in create_cluster: {e}")
        return None


def create_agent_for_cluster(
    client,
    package_id,
    cluster_id,
    cluster_owner_cap_id,
    model_id,
    model_owner_cap_id,
    name,
    role,
    goal,
    backstory,
    gas_budget=GAS_BUDGET,
):
    """
    Creates a new agent for the given cluster.
    This means that the agent does not live on-chain as a standalone object that
    other clusters could reference.

    :param client: The Sui client to use
    :param package_id: The ID of the package containing the "cluster" module
    :param cluster_id: The ID of the cluster to which the agent should be added
    :param cluster_owner_cap_id: The ID of the capability that owns the cluster
    :param model_id: The ID of the model to be used by the agent
    :param model_owner_cap_id: The ID of the capability that owns the model
    :param name: The name of the agent
    :param role: The role of the agent
    :param goal: The goal of the agent
    :param backstory: The backstory of the agent
    :param gas_budget: The gas budget for the transaction
    :return: True if the agent was successfully created, False otherwise
    """
    txn = SuiTransaction(client=client)

    try:
        result = txn.move_call(
            target=f"{package_id}::cluster::add_agent_entry",
            arguments=[
                ObjectID(cluster_id),
                ObjectID(cluster_owner_cap_id),
                ObjectID(model_id),
                ObjectID(model_owner_cap_id),
                SuiString(name),
                SuiString(role),
                SuiString(goal),
                SuiString(backstory),
            ],
        )
        result = txn.execute(gas_budget=gas_budget)
        if result.is_ok():
            return True
        print(f"Failed to add Agent: {result.result_string}")
        return False
    except Exception as e:
        print(f"Error in create_agent: {e}")
        return False


def create_task(
    client,
    package_id,
    cluster_id,
    cluster_owner_cap_id,
    name,
    agent_name,
    description,
    expected_output,
    prompt,
    context,
    gas_budget=GAS_BUDGET,
):
    """
    Creates a new task for the given cluster.
    Each task must be executed by an agent that is part of the cluster.

    Args:
        client: The Sui client to use
        package_id: The ID of the package containing the "cluster" module
        cluster_id: The ID of the cluster to which the agent should be added
        cluster_owner_cap_id: The ID of the capability that owns the cluster
        name: The name of the task
        agent_name: The name of the agent that should execute the task
        description: A description of the task
        expected_output: The expected output of the task
        prompt: The prompt to be given to the agent
        context: The context to be given to the agent
        gas_budget: The gas budget for the transaction

    Returns:
        True if the task was successfully created, False otherwise
    """
    txn = SuiTransaction(client=client)

    try:
        result = txn.move_call(
            target=f"{package_id}::cluster::add_task_entry",
            arguments=[
                ObjectID(cluster_id),
                ObjectID(cluster_owner_cap_id),
                SuiString(name),
                SuiString(agent_name),
                SuiString(description),
                SuiString(expected_output),
                SuiString(prompt),
                SuiString(context),
            ],
        )
        result = txn.execute(gas_budget=gas_budget)
        if result.is_ok():
            return True
        print(f"Failed to add Task: {result.result_string}")
        return False
    except Exception as e:
        print(f"Error in create_task: {e}")
        return False


def execute_cluster(
    client,
    package_id,
    cluster_id,
    input,
    gas_budget=GAS_BUDGET,
):
    """
    Begins execution of a cluster.
    Use the function [get_cluster_execution_response] to fetch the response of the execution
    in a blocking manner.
    :param client: The Sui client to use
    :param package_id: The ID of the package containing the "cluster" module
    :param cluster_id: The ID of the cluster to be executed
    :param input: The input to be given to the cluster
    :param gas_budget: The gas budget for the transaction (default = 1 SUI)

    :return: The cluster execution ID, or None if the transaction failed.
    """
    txn = SuiTransaction(client=client)

    try:
        result = txn.move_call(
            target=f"{package_id}::cluster::execute",
            arguments=[ObjectID(cluster_id), SuiString(input)],
        )
    except Exception as e:
        print(f"Error in execute_cluster: {e}")
        traceback.print_exc()
        return None

    result = txn.execute(gas_budget=gas_budget)

    if result.is_ok():
        if result.result_data.effects.status.status == "success":
            # just because it says "parsed_json" doesn't mean it's actually valid JSON apparently
            not_json = result.result_data.events[0].parsed_json
            created_event = ast.literal_eval(not_json.replace("\n", "\\n"))

            # There's going to be either field "execution" or "cluster execution"
            # because there are two events emitted in the tx.
            # We could check for the event name or just try both.
            execution_id = created_event.get(
                "execution", created_event.get("cluster_execution")
            )

            return execution_id
        else:
            error_message = result.result_data.effects.status.error
            print(f"Execute Cluster Transaction failed: {error_message}")
            return None
    else:
        print(f"Failed to create ClusterExecution: {result.result_string}")
        return None


def get_cluster_execution_response(
    client, execution_id, max_wait_time_s=180, check_interval_s=5
):
    """
    Fetches the response of a cluster execution.
    If the execution is not complete within the specified time, the function returns a timeout message.
    Args:
        client: The Sui client to use
        execution_id: The ID of the cluster execution to be fetched
        max_wait_time_s: The maximum time to wait for the execution to complete in seconds (default = 180)
        check_interval_s: The interval to check the status of the execution in seconds (default = 5)

    Returns:
        The response of the cluster execution, or a message indicating the reason for failure.
    """
    start_time = time.time()
    while time.time() - start_time < max_wait_time_s:
        try:
            # Create a GetObject builder
            get_object_builder = GetObject(object_id=ObjectID(execution_id))

            # Execute the query
            result = client.execute(get_object_builder)

            if result.is_ok():
                object_data = result.result_data
                if object_data and object_data.content:
                    fields = object_data.content.fields
                    status = fields.get("status")
                    if status == "SUCCESS":
                        return fields.get("cluster_response")
                    elif status == "FAILED":
                        return f"Execution failed: {fields.get('error_message')}"
                    elif status == "IDLE":
                        print("Execution has not started yet.")
                    elif status == "RUNNING":
                        until_timeout = max_wait_time_s - (time.time() - start_time)
                        print(
                            "Execution is still running, waiting... (%.2fs until timeout)"
                            % until_timeout
                        )
                    else:
                        return f"Unknown status: {status}"

                time.sleep(check_interval_s)
            else:
                return f"Failed to get object: {result.result_string}"

        except Exception as e:
            return f"Error checking execution status: {e}"

    return "Timeout: Execution did not complete within the specified time."
