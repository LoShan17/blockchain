from blockchain import Blockchain
import inspect

from uuid import uuid4
from flask import Flask, jsonify, request

app = Flask(__name__)
# globally unique address for this node
node_identifier = str(uuid4()).replace("-", "")
# blockchain instance
blockchain = Blockchain()


@app.route("/mine", methods=["GET"])
def mine():
    # running proof of work to get next proof
    last_block = blockchain.last_block
    last_proof = last_block["proof"]
    proof = blockchain.proof_of_work(last_proof)
    # sender is zero to signify that receiving node has mined the coin
    # node_identifier is defined globally above for every node
    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    # with the new proof we can now forge a block and add it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        "message": "New Block Forged",
        "index": block["index"],
        "transactions": block["transactions"],
        "proof": block["proof"],
        "previous_hash": block["previous_hash"],
    }

    return jsonify(response), 200


@app.route("/transactions/new", methods=["POST"])
def new_transactions():
    json_data = request.get_json()
    # check that required fields are in the posted data
    blockchain_signature = inspect.signature(blockchain.new_transaction)
    required = list(blockchain_signature.parameters.keys())
    if not all(k in json_data for k in required):
        return "Missing value in posted data", 400

    # if required data are there create a new transaction
    transaction_index = blockchain.new_transaction(*[json_data[k] for k in required])
    response = {"message": f"Transaction will be added to block {transaction_index}"}
    return jsonify(response), 201


@app.route("/chain", methods=["GET"])
def full_chain():
    response = {"chain": blockchain.chain, "chain_length": len(blockchain.chain)}
    return jsonify(response), 200


@app.route("/nodes/register", methods=["POST"])
def register_nodes():
    json_data = request.get_json()
    nodes = json_data.get("nodes")
    if nodes is None:
        return "Error, please provide a valid list of nodes", 400
    for node in nodes:
        blockchain.register_node(node)
    response = {
        "message": "new nodes have been added",
        "total_nodes": list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route("/nodes/resolve", methods=["GET"])
def consensus():
    node_chain_replaced = blockchain.resolve_conflicts()
    if node_chain_replaced:
        response = {
            "message": "current node's chain was replaced",
            "new_chain": list(blockchain.chain),
        }
    else:
        response = {
            "message": "current node's chain is authoritattive",
            "chain": list(blockchain.chain),
        }
    return jsonify(response), 200


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        current_port = int(sys.argv[1])
    else:
        print("Enter localhost port to spin server up:")
        current_port = int(input())
    app.run(host="0.0.0.0", port=current_port)
