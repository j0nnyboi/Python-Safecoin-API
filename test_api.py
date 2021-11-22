import argparse
import string
import random
import json
import time
import base58
from safecoin.keypair import Keypair
from safecoin.rpc.api import Client
from cryptography.fernet import Fernet

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


        


    

api_endpoint="https://api.devnet.safecoin.org"#point to devnet to test
Wallet_Address = "#WalletAddress"#add your wallet addrsss
topup = False #True if you want to topup
topupamount = 10 # amount to topup
WalletConnect(api_endpoint,Wallet_Address,topup,topupamount)
print("Success!")


