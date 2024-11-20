from pysui.sui.sui_txn.sync_transaction import SuiTransaction
from pysui.sui.sui_types.scalars import ObjectID, SuiU64, SuiU8, SuiString, SuiBoolean
from pysui.sui.sui_types.collections import SuiArray
import ast


def create_model(
    client,
    package_id,
    node_id,
    name,
    model_hash,
    url,
    token_price,
    capacity,
    num_params,
    description,
    max_context_length,
    is_fine_tuned,
    family,
    vendor,
    is_open_source,
    datasets,
):
    """
    Creates a new on-chain model object.
    Returns the model ID and the model owner capability ID.

    Parameters:
        client (SuiClient): The Sui client to use for the transaction.
        package_id (str): The ID of the package containing the `model` module.
        node_id (str): The ID of the node object where the model should be stored.
        name (str): The name of the model.
        model_hash (bytes): The hash of the model file.
        url (str): The URL where the model can be downloaded.
        token_price (int): The price of the model in tokens.
        capacity (int): The capacity of the model (i.e. the number of predictions it can make).
        num_params (int): The number of parameters in the model.
        description (str): A description of the model.
        max_context_length (int): The maximum length of the context that can be passed to the model.
        is_fine_tuned (bool): Whether the model is fine-tuned.
        family (str): The family of the model (e.g. BERT, RoBERTa, etc.).
        vendor (str): The vendor of the model (e.g. Hugging Face, PyTorch, etc.).
        is_open_source (bool): Whether the model is open-source.
        datasets (list[str]): The datasets that the model was trained on.
    """
    txn = SuiTransaction(client=client)

    args = [
        ObjectID(node_id),
        SuiString(name),
        SuiArray([SuiU8(b) for b in model_hash]),
        SuiString(url),
        SuiU64(token_price),
        SuiU64(capacity),
        SuiU64(num_params),
        SuiString(description),
        SuiU64(max_context_length),
        SuiBoolean(is_fine_tuned),
        SuiString(family),
        SuiString(vendor),
        SuiBoolean(is_open_source),
        SuiArray([SuiString(dataset) for dataset in datasets]),
    ]

    result = txn.move_call(
        target=f"{package_id}::model::create",
        arguments=args,
    )
    result = txn.execute(gas_budget=10000000)

    if result.is_ok():
        effects = result.result_data.effects
        if effects.status.status == "success":
            # just because it says "parsed_json" doesn't mean it's actually valid JSON apparently
            not_json = result.result_data.events[0].parsed_json
            created_event = ast.literal_eval(not_json.replace("\n", "\\n"))

            model_id = created_event["model"]
            model_owner_cap_id = created_event["owner_cap"]
            return model_id, model_owner_cap_id

    return None
