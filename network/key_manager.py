from network.ecc import ECCHandler


class KeyManager:
    """
    Stores ECC key pairs for all agents.
    """

    def __init__(self):
        self._keys = {}

    def register_agent(self, agent_name: str):
        """
        Generate and store an ECC key pair for an agent.
        """

        if agent_name not in self._keys:

            private_key, public_key = ECCHandler.generate_key_pair()

            self._keys[agent_name] = {
                "private": private_key,
                "public": public_key
            }

    def get_private_key(self, agent_name: str):
        """
        Return the private key of an agent.
        """

        if agent_name not in self._keys:
            raise ValueError(f"{agent_name} is not registered.")

        return self._keys[agent_name]["private"]

    def get_public_key(self, agent_name: str):
        """
        Return the public key of an agent.
        """

        if agent_name not in self._keys:
            raise ValueError(f"{agent_name} is not registered.")

        return self._keys[agent_name]["public"]

    def list_agents(self):
        """
        Return all registered agents.
        """

        return list(self._keys.keys())

    def has_agent(self, agent_name: str):
        """
        Check whether an agent is registered.
        """

        return agent_name in self._keys