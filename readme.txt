Название утилиты: tcping
Создатель: Пашков Данил

Утилита tcping является улучшенной версией утилиты ping.
Главным ее преимуществом перед ping является возможность отправки запросов на конкретный сокет.

Утилита умеет собирать информацию о задержке до получения ACK пакета, собирать статистику о кол-ве потерянных пакетов, max/min/avg времени получения ACK пакета, получать timeout когда порт не ответил.

При работе с утилитой можно использовать несколько флагов, позволяющих установить кол-во отправляемых пакетов, интервал, максимальное время timeout'а, конкретный порт на который будет отправлен запрос.