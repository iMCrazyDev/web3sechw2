rule onlyCreatorCanChangeCreator() {
    env e;
    address prev = creator(e);
    require e.msg.sender != prev;

    changeCreator(e);

    assert creator(e) == prev;
}

rule onlyCreatorCanMint(address addr, uint256 amount) {
    env e;
    require amount >= 0;
    require e.msg.sender != creator(e);

    uint256 balance = balanceOf(e, addr);

    mint(e, addr, amount);
    assert balance == balanceOf(e, addr);

}

/* ne ponyal o kakom "balanse" idet rech', sdelal po-svoemu
 tut eshche takoj bag, kak ya ponyal. Esli u tebya allowance na chuzhoj adres n,
 a ty hochesh' potratit' spend <= n, prichem spend > balanceOfAddress, to tranzakciya ne sovershitsya, no allowance potratitsya */
 
rule increaseAllowanceTest(address addr, uint256 amount) {
    env e;
    require amount >= 0;

    uint256 _allowance = allowance(e, e.msg.sender, addr);

    increaseAllowance(e, addr, amount);
    assert assert_uint256(_allowance + amount) == allowance(e, e.msg.sender, addr);
}

rule decreaseAllowanceTest(address addr, uint256 amount) {
    env e;
    require amount >= 0;

    uint256 _allowance = allowance(e, e.msg.sender, addr);

    require _allowance > amount;
    decreaseAllowance(e, addr, amount);
    assert assert_uint256(_allowance - amount) == allowance(e, e.msg.sender, addr);
}

methods
{
    // When a function is not using the environment (e.g., `msg.sender`), it can be
    // declared as `envfree`
    function balanceOf(address) external returns (uint) envfree;
    function allowance(address,address) external returns(uint) envfree;
    function totalSupply() external returns (uint) envfree;
}

rule onlyHolderCanChangeAllowance(address holder, address spender, method f) {

    // The allowance before the method was called
    env e;
    mathint allowance_before = allowance(holder, spender);


    calldataarg args;  // Arguments for the method f
    f(e, args);                        

    // The allowance after the method was called
    mathint allowance_after = allowance(holder, spender);

    assert allowance_after > allowance_before => e.msg.sender == holder,
        "only the sender can change its own allowance";

    // Assert that if the allowance changed then `approve` or `increaseAllowance` was called.
    assert (
        allowance_after > allowance_before =>
        (
            f.selector == sig:approve(address, uint).selector ||
            f.selector == sig:increaseAllowance(address, uint).selector
        )
    ),
    "only approve and increaseAllowance can increase allowances";
}

rule findChangeAllowance(address holder, address spender, method f) {

    // The allowance before the method was called
    env e;
    mathint allowance_before = allowance(holder, spender);


    calldataarg args;  // Arguments for the method f
    f(e, args);                        

    // The allowance after the method was called
    mathint allowance_after = allowance(holder, spender);

    assert allowance_after == allowance_before;  // esli upalo znachit pomenyalos, tak i naidem gde menyatsya
}

rule findChangeTotalSupply(method f) {
    env e;
    mathint total_before = totalSupply();


    calldataarg args; 
    f(e, args);                        

    mathint total_after = totalSupply();

    assert total_before == total_after;  // esli upalo znachit pomenyalos, tak i naidem gde menyatsya
}

