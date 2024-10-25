# Тестовое задание для Alber Blanc.

## Условие
Нужно написать код, который подключается в раздаче маркет даты binance usdt margin фьючерсов. 
<br /> https://binance-docs.github.io/apidocs/futures/en/#websocket-market-streams <br />
Устанавливается 5 коннекшенов. <br />
После подключения, в каждом коннекшене делается подписка на ws стрим BTCUSDT@bookTicker 
<br /> https://binance-docs.github.io/apidocs/futures/en/#individual-symbol-book-ticker-streams <br />
Нужно собрать сообщения за минуту, приходящие по каждому коннекшену. <br />
Далее для всех собранных сообщений посчитать задержку и построить функции распределения задержек каждого из коннекшенов на одном графике. Расчитать доли быстрых апдейтов по коннекшенам, "быстрым" считается коннекшен, получивший первым новый updateId. <br />
По полученным графикам сделать выводы, есть разница задержек между коннекшенами и почему (несколько причин возможных предложить). Провести стастистические тесты на равенство матожиданий и стандартных отклоненний задержек коннекшенов.

## Отчет

### Stdout после выполнения скрипта:
differtent update_ids count: 6559
fast updates for connection 1: 0
fast updates for connection 2: 0
fast updates for connection 3: 0
fast updates for connection 4: 0
fast updates for connection 5: 21
ANOVA test for means: F-statistic = 0.0008795037129418258, p-value = 0.9999984547227706
means do not differ
Levene test for variances: W-statistic = 0.0008795037129419233, p-value = 0.9999984547227706
standard deviations do not differ

### График:
![plot](https://github.com/user-attachments/assets/5110a792-edb6-4345-8052-6130eb1e9194)


### Анализ:
В результате можно сделать вывод, что Binance отдает данные в websocket практически без задержек. Возможно, это связано с низкой нагрузкой, так как замеры проводились в вечернее время, когда торги закрыты.
