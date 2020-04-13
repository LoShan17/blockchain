import hashlib
import time
import json
from urllib.parse import urlparse
import requests


class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # create the genesis block
        self.new_block(proof=100, previous_hash="0")
        self.nodes = set()

    def register_node(self, address: str) -> None:
        """
        add a new node to the set of nodes
        * address: <str> node address ex. 'http://192.168.0.5:5000'
        -> return: None
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url)

    def valid_chain(self, chain: list) -> bool:
        """
        determines if a given blockchain is valid
        * chain: <list> a blockchain
        -> return: <bool> True if valid, False if not
        """
        previous_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f"{previous_block}")
            print(f"{block}")
            print("\n------------\n")
            # check that the hash of the block is correct
            if block["previous_hash"] != self.hash(previous_block):
                return False
            # check that proof of work is correct
            if not self.valid_proof(previous_block["proof"], block["proof"]):
                return False
            previous_block = block
            current_index += 1
        return True

    def resolve_conflicts(self) -> bool:
        """
        this is the consensus algorithm that resolves conflicts
        by replacing local chain with the longest one in the network
        -> return: <bool> True if local chain is replaced, False if not
        """
        new_chain = None
        # with algorithm the node is looking for chains longer that it's chain
        max_length = len(self.chain)
        # grab and verify the chains from all the other nodes in the network
        for node in self.nodes:
            response = requests.get(f"http://{node}/chain")
            if response.status_code == 200:
                length = response.json()["length"]
                chain = response.json()["chain"]
                # check if the received chain is longer and valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # replace current node's chain if a new valid, longer chain was discovered
        if new_chain:
            self.chain = new_chain
            return True
        return False

    @property
    def last_block(self):
        return self.chain[-1]

    def new_block(self, proof: int, previous_hash: str = None) -> dict:
        """
        creates and returns a new block
        * proof: <int> proof given by 'proof of work' algorithm
        * (optional) previous_hash: <str> hash of previous block
        -> return: <dict> new block
        """
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time.time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1]),
        }
        # reset current transactions list
        self.current_transactions = []
        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """
        creates a new transaction to go into the next mined block
        transactions will be stored in current_transactions list
        until a new block is mined
        * sender: <str> address of the sender
        * recipient: <str> address of the recipient
        * amount: <int> amount
        -> return: <int> index of block holding this transaction
        """
        self.current_transactions.append(
            {"sender": sender, "recipient": recipient, "amount": amount}
        )
        return self.last_block["index"] + 1

    @staticmethod
    def hash(block: dict) -> str:
        """
        creates a SHA-256 of a block
        * block: <dict> block
        -> return: <str> string hash representation
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        """
        proof of work algorithm
        - finds the number p' such as hash(pp') contains 4 leading zeros
        - p is previous proof and p' is new proof
        * last_proof: <int> last proof
        -> return: <int> new proof
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int):
        """
        validates the proof answering the question: 
        does hash(proof, previous_proof) have 4 leading zeros?
        * last_proof: <int> last proof
        * proof: <int> current proof to be tested
        -> return: <bool> True if correct, False if not
        """
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
