import argparse
import string
import random
import json
import time
import base58
from safecoin.keypair import Keypair
from safecoin.rpc.api import Client
from metaplex.metadata import get_metadata
from cryptography.fernet import Fernet
from api.metaplex_api import MetaplexAPI

############################################## Config Wallet and or endpoint ################################################

api_endpoint="https://api.devnet.safecoin.org"
Wallet_Address = "3RvTHb2c3bAZgkfhqBhgyi2csQWixiypL2grjSkVDRBD"#"Wallet Addresss"
topup = True #True if you want to topup
topupamount = 10 # amount to topup


#There is no try again if fails, so if it failes at the moment you will need to try again, this might require afew attempts

##############################################################################################################################

def await_full_confirmation(client, txn, max_timeout=60):
    if txn is None:
        return
    elapsed = 0
    while elapsed < max_timeout:
        sleep_time = 1
        time.sleep(sleep_time)
        elapsed += sleep_time
        resp = client.get_confirmed_transaction(txn)
        while 'result' not in resp:
            resp = client.get_confirmed_transaction(txn)
        if resp["result"]:
            print(f"Took {elapsed} seconds to confirm transaction {txn}")
            break


def WalletConnect(api_endpoint,Wallet_Address,topup,topupamount):
    
    keypair = Keypair()
    cfg = {
        "PRIVATE_KEY": base58.b58encode(keypair.seed).decode("ascii"),
        "PUBLIC_KEY": str(keypair.public_key),
        "DECRYPTION_KEY": Fernet.generate_key().decode("ascii"),
    }
    api = MetaplexAPI(cfg)
    client = Client(api_endpoint)
    print("Connected to %s :" % api_endpoint, client.is_connected())
    if(client.is_connected()):
        
        if(topup == True):
            resp = {}
            while 'result' not in resp:
                resp = client.request_airdrop(Wallet_Address,topupamount * 1000000000)
            txn = resp['result']
            await_full_confirmation(client, txn)
            print(resp)
            print("Topup complete")
        resp = client.get_balance(Wallet_Address)
        print("balance = ", int(resp['result']['value']) / 1000000000)
        resp = client.get_account_info(Wallet_Address)
        print("")
        print("Wallet info ")
        print(resp)
        print("")
        print("Cluster Nodes ")
        print(client.get_cluster_nodes())
        print("")
        print("EPOCH info = ",client.get_epoch_info())
        
    else:
        print("cannot connect to ",api_endpoint)
        
        #resp = api.topup(api_endpoint,Wallet_Address,amount=20)
        #print(resp)


        
    """
    ##
    
    account = Keypair()
    cfg = {"PRIVATE_KEY": base58.b58encode(account.seed).decode("ascii"), "PUBLIC_KEY": Wallet_Address, "DECRYPTION_KEY": Fernet.generate_key().decode("ascii")}
    #api_endpoint = "https://api.devnet.safecoin.org/"
    Client(api_endpoint).request_airdrop(account.public_key, int(1e10))
    #{'jsonrpc': '2.0', 'result': '4ojKmAAesmKtqJkNLRtEjdgg4CkmowuTAjRSpp3K36UvQQvEXwhirV85E8cvWYAD42c3UyFdCtzydMgWokH2mbM', 'id': 1}
    metaplex_api = MetaplexAPI(cfg)
    seller_basis_fees = 0 # value in 10000
    REC = metaplex_api.deploy(api_endpoint, "A"*32, "A"*10, seller_basis_fees)
    print(REC)
    #'{"status": 200, "contract": "7bxe7t1aGdum8o97bkuFeeBTcbARaBn9Gbv5sBd9DZPG", "msg": "Successfully created mint 7bxe7t1aGdum8o97bkuFeeBTcbARaBn9Gbv5sBd9DZPG", "tx": "2qmiWoVi2PNeAjppe2cNbY32zZCJLXMYgdS1zRVFiKJUHE41T5b1WfaZtR2QdFJUXadrqrjbkpwRN5aG2J3KQrQx"}'

    """
    

def test(api_endpoint="https://api.devnet.safecoin.org/"):
    keypair = Keypair()
    cfg = {
        "PRIVATE_KEY": base58.b58encode(keypair.seed).decode("ascii"),
        "PUBLIC_KEY": str(keypair.public_key),
        "DECRYPTION_KEY": Fernet.generate_key().decode("ascii"),
    }
    api = MetaplexAPI(cfg)
    client = Client(api_endpoint)
    resp = {}
    while 'result' not in resp:
        resp = client.request_airdrop(keypair.public_key, int(1e9))
    print("Request Airdrop:",keypair.public_key, resp)
    txn = resp['result']
    await_full_confirmation(client, txn)
    letters = string.ascii_uppercase
    name = ''.join([random.choice(letters) for i in range(32)])
    symbol = ''.join([random.choice(letters) for i in range(10)])
    print("Name:", name)
    print("Symbol:", symbol)
    # added seller_basis_fee_points
    deploy_response = json.loads(api.deploy(api_endpoint, name, symbol, 0))
    print("Deploy:", deploy_response)
    assert deploy_response["status"] == 200
    contract = deploy_response.get("contract")
    print("contract", contract)
    print(get_metadata(client, contract))
    wallet = json.loads(api.wallet())
    address1 = wallet.get('address')
    encrypted_pk1 = api.cipher.encrypt(bytes(wallet.get('private_key')))
    topup_response = json.loads(api.topup(api_endpoint, address1))
    print(f"Topup {address1}:", topup_response)
    assert topup_response["status"] == 200
    mint_to_response = json.loads(api.mint(api_endpoint, contract, address1, "https://arweave.net/1eH7bZS-6HZH4YOc8T_tGp2Rq25dlhclXJkoa6U55mM/"))
    print("Mint:", mint_to_response)
    #await_full_confirmation(client, mint_to_response['tx'])
    assert mint_to_response["status"] == 200
    print(get_metadata(client, contract))
    wallet2 = json.loads(api.wallet())
    address2 = wallet2.get('address')
    encrypted_pk2 = api.cipher.encrypt(bytes(wallet2.get('private_key')))
    print(client.request_airdrop(api.public_key, int(1e10)))
    topup_response2 = json.loads(api.topup(api_endpoint, address2))
    print(f"Topup {address2}:", topup_response2)
    #await_full_confirmation(client, topup_response2['tx'])
    assert topup_response2["status"] == 200
    send_response = json.loads(api.send(api_endpoint, contract, address1, address2, encrypted_pk1))
    assert send_response["status"] == 200
    #await_full_confirmation(client, send_response['tx'])
    burn_response = json.loads(api.burn(api_endpoint, contract, address2, encrypted_pk2))
    print("Burn:", burn_response)
    #await_full_confirmation(client, burn_response['tx'])
    assert burn_response["status"] == 200
    print("Success!")


#WalletConnect(api_endpoint,Wallet_Address,topup,topupamount)
print("Success! topping up wallet")

print("Now going to mint transfer and burn")
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--network", default=None)
    args = ap.parse_args()
    if args.network == None or args.network == 'devnet':
        test()
    elif args.network == 'devnet':
        test(api_endpoint="https://api.devnet.safecoin.org/")
    elif args.network == 'mainnet':
        test(api_endpoint="https://api.mainnet-beta.safecoin.org/")
    else:
        print("Invalid network argument supplied")


