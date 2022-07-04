# Spideriment-NG

**Spideriment-NG** _(spider + experiment "Next Generation")_ is a cloud-first, scalable and modular 
**web spider/crawler/indexer daemon** programmed in Python.

_NOTE:_ The reason why this program has _Next Generation_ in its name is that it is a successor to 
[Spideriment](https://github.com/vitlabuda/spideriment), a web crawler programmed by me approximately a year ago,
which offers mostly the same "core" functionality, but it suffers from very limited flexibility, limited configuration 
options and poor software design/architecture.
Therefore, I decided to rewrite the program from scratch, adding some features on that occasion.





## Crawled information

- Title
- Description
- Content snippets
  - ... of various types/priorities (headings of different levels, emphasized text, regular text, list item text etc.)
- File type
- Language
- Author
- Keywords
- Links
- Images
  - ... only their URLs, alt texts and title texts are crawled, and not the images themselves!





## Features & characteristics

- **Cloud-first & scalable architecture**
  - May run in multiple worker processes
  - Each worker process makes use of `asyncio` to further increase its performance and effectivity
  - Multiple instances may share the same database and cooperate in this way


- **Highly-abstract modular design**
  - Fetchers:
    - `internet` – supports HTTP/S and SOCKS4/5 proxies → the crawler may (should) be used with **Tor**
  - Databases:
    - `mysql` – supports both MySQL and MariaDB
  - Document parsers:
    - `html`
  - Robot caches:
    - `memory` – caches _robots.txt_ files in a dictionary inside the crawler
    - `memcached`


- **Extensive configuration options**
  - Various size and length limits
  - Regex-based sequences of `allow`/`block` filters for various document properties (URLs, titles, content snippets etc.)
  - Uniform way of configuring modules


- **Supports `robots.txt`**
  - Both disallows and delays (`Crawl-Delay`, `Request-Rate`) are respected


- Architecture-wise, the program makes use of:
  - Object-oriented design
  - Dependency injection (DI) – [`sidein`](https://github.com/vitlabuda/sidein)
  - Cooperative multitasking – `asyncio`





## DISCLAIMER
**Since the crawler is completely automatic, it may visit websites which are illegal in your country or which could 
cause your IP address to be placed on a blocklist ("honeypots"). Even though the configurable filters the program offers
can be used to lower the risk, nothing is guaranteed to be working correctly in 100% of cases. 
It is also RECOMMENDED to route the crawler's traffic through Tor (by using the proxy feature of the `internet` fetcher 
module), although be aware that using Tor is also illegal in some countries.**

**Always use this program with caution and within the law! As is stated in the [license](LICENSE), the author is not 
liable for any damages or legal issues caused by this program and its use!**





## Deployment

### Linux
The program requires **Python 3.9 or above**.

#### 1. Install the dependencies
Using `apt` (Debian, Ubuntu etc.):
```shell
sudo apt update
sudo apt install python3 python3-pip python3-virtualenv virtualenv
```

Using `dnf` (Fedora, CentOS, RHEL etc.):
```shell
sudo dnf install python3 python3-pip python3-virtualenv virtualenv
```

#### 2. Configure the crawler
```shell
cd src/
cp spideriment-ng.example.toml spideriment-ng.toml
nano spideriment-ng.toml  # Use the editor you prefer...
```
The [`spideriment-ng.example.toml`](src/spideriment-ng.example.toml) file contains an example configuration of this program.

#### 3. Run the crawler
```shell
cd src/
./run_spideriment_ng.sh spideriment-ng.toml
```
The [`run_spideriment_ng.sh`](src/run_spideriment_ng.sh) bash script downloads the program's Python dependencies 
(as per [requirements.txt](src/requirements.txt)) using `pip` into a newly created `virtualenv` and starts it.

Keep in mind that the script changes the working directory to the directory where the script is located; therefore, 
**relative configuration file paths are relative to the [`src/`](src) directory!**

#### 4. Stop the crawler
To stop the crawler, send a `SIGTERM`, `SIGINT` or `SIGHUP` signal to the supervisor process (the first process to have
started), for example by pressing **Ctrl+C** in the terminal it is running in. Keep in mind that the program shuts down
only after all its workers finish processing their currently crawled documents, which might take some time!


### Docker

**Coming soon!**





## Licensing
This project is licensed under the **3-clause BSD license** – see the [LICENSE](LICENSE) file.

In addition, this project uses some third-party open-source components – see the 
[THIRD-PARTY-LICENSES](THIRD-PARTY-LICENSES) file.

Programmed by **[Vít Labuda](https://vitlabuda.cz/)**.
