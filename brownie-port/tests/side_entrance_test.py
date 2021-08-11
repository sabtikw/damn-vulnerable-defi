import pytest

from brownie import accounts, SideEntranceLenderPool

@pytest.fixture(scope='module')
def deployer(accounts):
    return accounts[0]

@pytest.fixture(scope='module')
def attacker(accounts):
    return accounts[1]


@pytest.fixture(scope='module')
def someUser(accounts):
    return accounts[2]




@pytest.fixture(scope='module')
def pool(deployer):
    return SideEntranceLenderPool.deploy({'from': deployer})




@pytest.fixture(scope='module',autouse=True)
def setup(pool,deployer): 
    ''' [Challenge] side entrance '''

    ETHER_IN_POOL = 1000e18
    
    # SETUP SCENARIO
    pool.deposit({'from':deployer, 'value':ETHER_IN_POOL})

    assert pool.balance() == ETHER_IN_POOL



def exploit_test(pool,attacker):
    #/** YOUR EXPLOIT GOES HERE */
    pass
    

def test_success(pool,attacker):

    assert pool.balance() == 0

    assert attacker.balance > 1000e18

       

