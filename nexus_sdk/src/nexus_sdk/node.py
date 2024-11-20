from pysui.sui.sui_txn.sync_transaction import SuiTransaction
from pysui.sui.sui_types.scalars import SuiU64


def create_node(client, package_id, name, node_type, gpu_memory):
    """
    Creates a new node owned object.

    Args:
        client (SuiClient): A Sui client.
        package_id (str): The ID of the package containing the node module.
        name (str): The name of the node.
        node_type (str): The type of the node.
        gpu_memory (int): The amount of GPU memory in MB required by the node.

    Returns:
        str: The ID of the created node object.
    """
    txn = SuiTransaction(client=client)

    result = txn.move_call(
        target=f"{package_id}::node::create",
        arguments=[name, node_type, SuiU64(gpu_memory), "c", []],
    )
    result = txn.execute(gas_budget=10000000)

    if result.is_ok() or result._data.succeeded:
        node_id = result._data.effects.created[0].reference.object_id
        return node_id
    else:
        print(f"Failed to create node: {result.result_string}")
        return None
