from constants import *
import subprocess
import json
from web3 import Web3
from dotenv import load_dotenv
from eth_account import Account
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from bit import PrivateKeyTestnet
import bit

load_dotenv()




def derive_wallets(coin):
    if (coin == BTCTEST):
        output_01 = subprocess.run(['./derive','-g', f'--mnemonic={mnemonic}', f'--coin={BTCTEST}', '--numderive=3', '--format=json'], text=True, capture_output=True)
        return(json.loads(output_01.stdout))
    elif (coin == ETH):
        output_02 = subprocess.run(['./derive','-g', f'--mnemonic={mnemonic}', f'--coin={ETH}', '--numderive=3', '--format=json'], text=True, capture_output=True)
        return(json.loads(output_02.stdout))


Coins = {"btc-test" : derive_wallets(BTCTEST), "eth" : derive_wallets(ETH)}


btc_test_privkeys = {"privkey_01": Coins['btc-test'][0]['privkey'],"privkey_02": Coins['btc-test'][1]['privkey'],"privkey_03": Coins['btc-test'][2]['privkey']}

eth_privkeys = {"privkey_01": Coins['eth'][0]['privkey'],"privkey_02": Coins['eth'][1]['privkey'],"privkey_03": Coins['eth'][2]['privkey']}



def priv_key_to_account(coin, priv_key):
    if (coin == BTCTEST):
        btctest_account = PrivateKeyTestnet(priv_key)
        return(btctest_account)
    elif (coin == ETH):
        eth_account = Account.privateKeyToAccount(priv_key)
        return(eth_account)


btc_test_accounts = {
    "account_01": priv_key_to_account(BTCTEST, btc_test_privkeys["privkey_01"]), 
    "account_02": priv_key_to_account(BTCTEST, btc_test_privkeys["privkey_02"]), 
    "account_03": priv_key_to_account(BTCTEST, btc_test_privkeys["privkey_03"])  
}

eth_accounts = {
    "account_01": priv_key_to_account(ETH, eth_privkeys["privkey_01"]), 
    "account_02": priv_key_to_account(ETH, eth_privkeys["privkey_02"]), 
    "account_03": priv_key_to_account(ETH, eth_privkeys["privkey_03"])  
}



def create_tx(coin, account, to, amount):
    if (coin == BTCTEST):
        btc_tx = PrivateKeyTestnet.prepare_transaction(account.address, [(to.address, amount, BTC)])
        return(btc_tx)
    elif (coin == ETH):
        gas_estimate = w3.eth.estimateGas({"from": account.address,"to": to,"value": amount})
        return({"to": to,"from": account.address,"value": amount,"gas": gas_estimate,"gas_price": w3.eth.gasPrice,"nonce":w3.eth.getTransactionCount(account.address),"chain_id": w3.eth.chainId})

    
    
def send_tx(coin, account, to, amount):
    if (coin == BTCTEST):
        tx_data = create_tx(coin, account, to, amount)
        signed_tx = account.sign_transaction(tx_data)
        result = bit.network.NetworkAPI.broadcast_tx_testnet(signed_tx)
        return(result)
    elif (coin == ETH):
        raw_tx = create_tx(coin, account, to, amount)
        signed = account.sign_transaction(raw_tx)
        result = w3.eth.sendRawTransaction(signed.rawTransaction)
        return(result.hex())

print(send_tx(BTCTEST, btc_accounts["account_01"], btc_accounts["account_02"], 0.00003))



print(send_tx(ETH, eth_accounts["account_01"], eth_accounts["account_02"], 200000000000000))