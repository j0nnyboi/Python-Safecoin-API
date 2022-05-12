import argparse
import string
import random
import json
import time
import base58
from safecoin.keypair import Keypair
from safecoin.rpc.api import Client
from ledaplex.metadata import get_metadata,get_metadata_account
from cryptography.fernet import Fernet
from api.ledaplex_api import LedaplexAPI

############################################## Config Wallet and or endpoint ################################################

api_endpoint="https://api.testnet.safecoin.org"
Wallet_Address = "3RvTHb2c3bAZgkfhqBhgyi2csQWixiypL2grjSkVDRBD"#"Wallet Addresss"
Mint_Address = "9NuJbgzZA4JQfzDi2zKqJUKDWLhLcPLLoySCTDs43toS"#NFT Mint Address
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
    print("Connecting to Safecoin chain")
    client = Client(api_endpoint)
    print("Connected to %s :" % api_endpoint, client.is_connected())
    print("")
    if(client.is_connected()):
        
        if(topup == True):
            resp = {}
            while 'result' not in resp:
                resp = client.request_airdrop(Wallet_Address,topupamount * 1000000000)
            txn = resp['result']
            await_full_confirmation(client, txn)
            #print(resp)
            print("Topup complete")
            print("")
        resp = client.get_balance(Wallet_Address)
        print("balance = ", int(resp['result']['value']) / 1000000000)
        resp = client.get_account_info(Wallet_Address)
        print("")
        print("Wallet info ")
        #print(resp)
        print("")
        print("Cluster Nodes ")
        print(client.get_cluster_nodes())
        print("")
        print("EPOCH info = ",client.get_epoch_info())
        print("")
        
    else:
        print("cannot connect to ",api_endpoint)
        
        #resp = api.topup(api_endpoint,Wallet_Address,amount=20)
        #print(resp)


    

def test_mint_tran_burn(api_endpoint="https://api.testnet.safecoin.org/"):
    keypair = Keypair()
    cfg = {
        "PRIVATE_KEY": base58.b58encode(keypair.seed).decode("ascii"),
        "PUBLIC_KEY": str(keypair.public_key),
        "DECRYPTION_KEY": Fernet.generate_key().decode("ascii"),
    }
    api = LedaplexAPI(cfg)
    client = Client(api_endpoint)
    resp = {}
    while 'result' not in resp:
        resp = client.request_airdrop(keypair.public_key, int(1e9))
    #print("Request Airdrop:",keypair.public_key, resp)    
    txn = resp['result']
    await_full_confirmation(client, txn)
    letters = string.ascii_uppercase
    name = ''.join([random.choice(letters) for i in range(32)])
    symbol = ''.join([random.choice(letters) for i in range(10)])
    print("Name:", name)
    print("Symbol:", symbol)
    print("")
    # added seller_basis_fee_points
    deploy_response = json.loads(api.deploy(api_endpoint, name, symbol, 0))
    #print("Deploy:", deploy_response)
    assert deploy_response["status"] == 200
    contract = deploy_response.get("contract")
    print("contract", contract)
    print("")
    print(get_metadata(client, contract))
    wallet = json.loads(api.wallet())
    address1 = wallet.get('address')
    encrypted_pk1 = api.cipher.encrypt(bytes(wallet.get('private_key')))
    topup_response = json.loads(api.topup(api_endpoint, address1))
    #print(f"Topup {address1}:", topup_response)
    assert topup_response["status"] == 200
    mint_to_response = json.loads(api.mint(api_endpoint, contract, address1, "https://arweave.net/1eH7bZS-6HZH4YOc8T_tGp2Rq25dlhclXJkoa6U55mM/"))
    print("Mint:", mint_to_response)
    print("")
    #await_full_confirmation(client, mint_to_response['tx'])
    assert mint_to_response["status"] == 200
    #print(get_metadata(client, contract))
    wallet2 = json.loads(api.wallet())
    address2 = wallet2.get('address')
    encrypted_pk2 = api.cipher.encrypt(bytes(wallet2.get('private_key')))
    #print(client.request_airdrop(api.public_key, int(1e10)))
    topup_response2 = json.loads(api.topup(api_endpoint, address2))
    #print(f"Topup {address2}:", topup_response2)
    #await_full_confirmation(client, topup_response2['tx'])
    assert topup_response2["status"] == 200
    send_response = json.loads(api.send(api_endpoint, contract, address1, address2, encrypted_pk1))
    assert send_response["status"] == 200
    #await_full_confirmation(client, send_response['tx'])
    burn_response = json.loads(api.burn(api_endpoint, contract, address2, encrypted_pk2))
    print("Burn:", burn_response)
    print("")
    #await_full_confirmation(client, burn_response['tx'])
    assert burn_response["status"] == 200
    print("Create, Mint, Send, Burn, Success!")
    
def test_get_mintData():
    client = Client(api_endpoint)
    print(get_metadata(client,Mint_Address))#gets metadata for a given mint address
    print(get_metadata_account(Mint_Address))



######## Safecoin Chain only #####################################
#WalletConnect(api_endpoint,Wallet_Address,topup,topupamount)
print("")
print("Success! topping up wallet")
print("")

################ metaplex programs ###############################
print("Now going to mint transfer and burn")
print("")
#test_mint_tran_burn()
print("")
print("Getting Mint data")
test_get_mintData()
print("Completed")




