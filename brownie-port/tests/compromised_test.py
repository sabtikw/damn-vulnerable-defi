import pytest

from brownie import Exchange, DamnValuableNFT, TrustfulOracle, TrustfulOracleInitializer, accounts


@pytest.fixture(scope='module')
def deployer():
    return accounts[0]

@pytest.fixture(scope='module')
def attacker():
    return accounts[1]

@pytest.fixture(scope='module')
def sources():
    return [
        '0xA73209FB1a42495120166736362A1DfA9F95A105',
        '0xe92401A4d3af5E446d93D11EEc806b1462b39D15',
        '0x81A5D6E50C214044bE44cA0CB057fe119097850c'
    ]

@pytest.fixture(scope='module')
def oracle(deployer,sources):

    
    INITIAL_NFT_PRICE = 999e18


    return TrustfulOracle.at(TrustfulOracleInitializer.deploy(
            sources,
            ['DVNFT', 'DVNFT', 'DVNTF'],
            [INITIAL_NFT_PRICE, INITIAL_NFT_PRICE, INITIAL_NFT_PRICE],
            {'from': deployer}
        ).oracle()
        )
        
    

@pytest.fixture(scope='module')
def exchange(oracle, deployer):
    # Deploy the exchange and get the associated ERC721 token
    EXCHANGE_INITIAL_ETH_BALANCE = 10000e18

    return Exchange.deploy(oracle.address,{'from':deployer,'value':EXCHANGE_INITIAL_ETH_BALANCE})


@pytest.fixture(scope='module')
def token(exchange, deployer):
    return DamnValuableNFT.at(exchange.address.token())


@pytest.fixture(scope='module',autouse=True)
def setup(sources,deployer):

    # Fund the trusted source addresses
    for source in sources:

        deployer.transfer(to=source,amount='5 ether')

def test_exploit(oracle,exchange,sources,attacker):
    # Exploit goes here
    pass
    


def test_success(exchange,attacker):

    EXCHANGE_INITIAL_ETH_BALANCE = 10000e18

    assert exchange.balance() == 0

    assert attacker.balance() == EXCHANGE_INITIAL_ETH_BALANCE
