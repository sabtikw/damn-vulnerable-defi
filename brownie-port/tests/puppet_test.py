import pytest

import json

from brownie import DamnValuableToken, PuppetPool, web3, Contract, chain



intialAttackerEthBalance = 1
# Calculates how much ETH (in wei) Uniswap will pay for the given amount of tokens
def calculateTokenToEthInputPrice(tokensSold, tokensInReserve, etherInReserve):

    return tokensSold * 997 * etherInReserve / tokensInReserve * 1000 + tokensSold * 997
    


@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[1]


@pytest.fixture(scope='module')
def token(deployer):
    return DamnValuableToken.deploy({'from':deployer})


@pytest.fixture(scope='module')
def exchangeTemplate(deployer,Contract):

    contractArtifacts = json.loads(open("../build-uniswap-v1/UniswapV1Exchange.json").read())
    contract = web3.eth.contract(abi=contractArtifacts['abi'],bytecode=contractArtifacts['bytecode'])
    tx_hash = contract.constructor().transact({'from': deployer.address})
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)

    return Contract.from_abi(
        "UniswapV1Exchange",
        tx_receipt['contractAddress'],
        contractArtifacts['abi']
        )


@pytest.fixture(scope='module')
def uniswapFactory(deployer,Contract):

    contractArtifacts = json.loads(open("../build-uniswap-v1/UniswapV1Factory.json").read())
    contract = web3.eth.contract(abi=contractArtifacts['abi'],bytecode=contractArtifacts['bytecode'])
    tx_hash = contract.constructor().transact({'from': deployer.address})
    tx_receipt = web3.eth.get_transaction_receipt(tx_hash)

    return Contract.from_abi(
        "UniswapV1Factory",
        tx_receipt['contractAddress'],
        contractArtifacts['abi']
        )


@pytest.fixture(scope='module')
def uniswapExchange(token,uniswapFactory,exchangeTemplate,deployer):
    
    uniswapFactory.initializeFactory(exchangeTemplate.address, {'from': deployer})

    exchangeAddress = uniswapFactory.createExchange(token.address,{'from':deployer})
    # interface from abi ? might work ? I need to use at without deploy
    uniswapExchange = Contract.from_abi('UniswapExchange',
    exchangeAddress.events[0]['exchange'],
    abi=json.loads(open("../build-uniswap-v1/UniswapV1Exchange.json").read())['abi']
    )

    return uniswapExchange


@pytest.fixture(scope='module')
def lendingPool(token,uniswapExchange,deployer):

    return PuppetPool.deploy(token.address,uniswapExchange.address, {'from':deployer})

@pytest.fixture(scope='module',autouse=True)
def setup(uniswapFactory,exchangeTemplate,uniswapExchange,token,lendingPool,deployer,attacker):

    UNISWAP_INITIAL_TOKEN_RESERVE = 10e18
    UNISWAP_INITIAL_ETH_RESERVE = 10e18
    POOL_INITIAL_TOKEN_BALANCE = 10000e18
    ATTACKER_INITAL_TOKEN_BALANCE = 100e18

   

    
    token.approve(uniswapExchange.address,UNISWAP_INITIAL_TOKEN_RESERVE,{'from':deployer})

    deadline = chain[-1].timestamp * 2

    uniswapExchange.addLiquidity(0,
        UNISWAP_INITIAL_TOKEN_RESERVE,
        deadline,
        {'from':deployer,'value': UNISWAP_INITIAL_ETH_RESERVE})


    uniswapExchange.getTokenToEthInputPrice('1 ether') == calculateTokenToEthInputPrice(1e18,
                                                                                        UNISWAP_INITIAL_TOKEN_RESERVE,
                                                                                         UNISWAP_INITIAL_ETH_RESERVE
                                                                                         )
    token.transfer(attacker.address, ATTACKER_INITAL_TOKEN_BALANCE, { 'from': deployer })
    
    token.transfer(lendingPool.address, POOL_INITIAL_TOKEN_BALANCE, { 'from': deployer })

    assert lendingPool.computeOraclePrice() == 1


@pytest.fixture(scope='module')
def attackerBalance(attacker):
    # Track attacker's initial ETH balance (to ensure it doesn't decrease)
   return attacker.balance()

def test_exploit(uniswapExchange,token,lendingPool,attacker,attackerBalance):
    # Exploit goes here
    
    pass
    


def test_success(token,lendingPool,attacker,attackerBalance):

    UNISWAP_INITIAL_TOKEN_RESERVE = 10e18
    UNISWAP_INITIAL_ETH_RESERVE = 10e18
    POOL_INITIAL_TOKEN_BALANCE = 10000e18
    

    global intialAttackerEthBalance

    assert token.balanceOf(attacker.address) >= POOL_INITIAL_TOKEN_BALANCE
    assert token.balanceOf(lendingPool.address) == 0
    assert attackerBalance == calculateTokenToEthInputPrice(1e18,
                                                                UNISWAP_INITIAL_TOKEN_RESERVE,
                                                                UNISWAP_INITIAL_ETH_RESERVE
                                                            )