from cli_cluster import CliCluster

class ExampleRunner:
    def __init__(self,
        client,
        package_id,
        model_id,
        model_owner_cap_id
    ):
        self.client = client
        self.package_id = package_id
        self.model_id = model_id
        self.model_owner_cap_id = model_owner_cap_id
        self.cli_cluster = CliCluster(
            self.client,
            self.package_id,
            self.model_id,
            self.model_owner_cap_id
        )

