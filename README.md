<a id="readme-top"></a>

[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![MIT License][license-shield]][license-url]
[![Telegram][telegram-shield]][telegram-url]
[![Python][Python.com]][Python-url]

<h3 align="center">Telegram Text Dumper</h3>
  <p align="center">
    Export text from Telegram channels and forum topics into one TXT file.
  <br />
  <a href="https://github.com/Argona7/TgDowloander/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
  ·
  <a href="https://github.com/Argona7/TgDowloander/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>


<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#key-feature">Key Feature</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#env-management">Env Management</a></li>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#quick-start">Quick Start</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#faq">FAQ</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

## About The Project
![TgDowloander][product-screenshot]

A Python script that downloads **all content** from user Telegram sources:
- additional channels `@username` / `https://t.me/username `;
- main groups by name id `-100...` and **links like** `https://t.me/c /<numbers>/<identifier>`;
- **for-topics** (message topics) — you can select the desired topic or upload the entire for.

Powered by [Pyrogram 2.x](https://docs.pyrogram.org /) + [TgCrypto](https://github.com/pyrogram/tgcrypto ), logs — via [logura](https://github.com/Delgan/loguru ).
The information is saved in a single TXT (UTF-8, without specification) as ** from text to new**, with the last `message ID` specified.

<p align="right">(<a href="#readme-top">go back to the beginning</a>)</p>

### Key Feature

- Channels and forum-topics (threads)
- Understanding private links `t.me/c /<digits>/<id>`
- Filter by date range (`YYYY-MM-DD..YYYY-MM-DD`) and `LIMIT`
- Resume by the last recorded `message_id`
- Skipping service/empty messages, normalization of hyphenation/spaces
- Bypassing FLOOD_WAIT / RPCError (retrace) + beautiful logs

<p align="right">(<a href="#readme-top">back to top</a>)</p>

# Getting Started

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Env Management

| Setting              | Description                                                                                 |
|----------------------|---------------------------------------------------------------------------------------------|
| **API_ID** | API ID from [my.telegram.org ](https://my.telegram.org ) |
| **API_HASH**         | API Hash from [my.telegram.org ](https://my.telegram.org ) |
| **SESSION_NAME**     | Name of the local session (will create a file `<name>.session`)                                        |
| **CHANNEL**          | `@username`, `https://t.me/username`, `-100...` or `https://t.me/c /<digits>/<id>`          |
| **OUTPUT_FILE**      | The path to the resulting `.txt` (for example, `./dump/output.txt `) |
| **DATE_RANGE**       | _(optional)_ `YYYY-MM-DD..YYYY-MM-DD` (inclusive) or one date `YYYY-MM-DD`                 |
| **LIMIT**            | _(optional)_ maximum number of suitable messages |
| **PAGE_SIZE**        | _(optional)_ sample size per request (100-200 recommended)                              |
| **PROGRESS_EVERY** | _(optional)_ log progress for every N processed messages |
| **LOG_LEVEL**        | _(optional)_ `DEBUG` / `INFO` / `WARNING` / `ERROR`                                              |
| **LOG_FILE**         | _(optional)_ path to the log file (if you want to write logs to the file as well)                             |

Example: `examples/.env.example' (copy to `.env` and fill in).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Prerequisites
> [!IMPORTANT]  
> Python is recommended **3.9+** (tested on 3.11/3.13).

Check the version:
- Windows: `python --version`  
- macOS/Linux: `python3 --version`

Have a Telegram API ID/Hash (entered on [my.telegram.org ](https://my.telegram.org )).

### Quick Start📚

1. Clone the repo
   ```sh
   git clone https://github.com/Argona7/TgDowloander.git
   ```
    ```sh
   cd TgDowloander
   ```
2. Set environment variables
   - Windows OS
   ```sh
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
   - Linux OS
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   ```

3. Edit your .env configuration, tutorial: ([#env-management](#env-management))
    ```sh
   cp examples/.env.example .env     
    notepad .env          # Windows OS
    nano .env             # Linux OS
    ```
   
4. Run python file according to your operating system.
    ```sh
   python main.py
    ```
<p align="right">(<a href="#readme-top">back to top</a>)</p>


## FAQ

After the script is successfully installed, you will see four options:

1. **Fill in the .env (especially API_ID, API_HASH, SESSION_NAME, CHANNEL, OUTPUT_FILE).**
2. **Run the bot**
3. **If the source is a forum (threads), the script will show a list of topics and ask you to select
— you can enter a number from the list or top_message_id. An empty input is the unloading of the entire history.**

### Result format

```commandline
---
id: 12345
date: 2024-12-31T23:59:59Z
author: @author_username
text:
text of the post...

---
id: 12346
date: 2025-01-01T00:00:10Z
author: channel N
text:
text of the post...
```

> [!TIP]
> For private supergroups with links like https://t.me/c /<digits>/<id> it is enough to specify this link in the CHANNEL.
If you use -100..., but you get an access error, open this chat once in Telegram under this account.


<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Troubleshooting & FAQ
Q: **USERNAME_INVALID / Peer id invalid: -100...**

A: You are not in the chat / no access / Pyrogram does not know access_hash. Log in to the chat in the official Telegram client, then re-launch. For -100... the script itself will go through the dialogs and cache them.

---
Q: **Permission denied / private channel**

A: The script uploads only what the account has access to. Join the channel/chat.

---
Q: **Viewed N, saved 0**

A: All messages turned out to be without text/signature, did not get to the DATE_RANGE/topic_id, or were already saved (resuming). Turn on LOG_LEVEL=DEBUG and you will see the reason counter in [skips].

---
Q: **FLOOD_WAIT**

A: The script automatically waits for the required number of seconds and continues. Just wait, it's okay.

---
Q: **Does not see .env**

A: Check that.env is at the root of the project (where main.py ) or next to the script, without the BOM (UTF-8).
An example of a correct string: API_ID=123456 (without spaces around =).
## License

Distributed under the MIT License.
The GNU General Public License is a free, copyleft license for software and other kinds of works.

More Info on [LICENSE](https://github.com/Argona7/TgDowloander/blob/main/LICENSE) file.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

[forks-shield]: https://img.shields.io/github/forks/Argona7/TgDowloander.svg?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0Ij48cGF0aCBkPSJNOC43NSAxOS4yNWEzLjI1IDMuMjUgMCAxIDEgNi41IDAgMy4yNSAzLjI1IDAgMCAxLTYuNSAwWk0xNSA0Ljc1YTMuMjUgMy4yNSAwIDEgMSA2LjUgMCAzLjI1IDMuMjUgMCAwIDEtNi41IDBabS0xMi41IDBhMy4yNSAzLjI1IDAgMSAxIDYuNSAwIDMuMjUgMy4yNSAwIDAgMS02LjUgMFpNNS43NSA2LjVhMS43NSAxLjc1IDAgMSAwLS4wMDEtMy41MDFBMS43NSAxLjc1IDAgMCAwIDUuNzUgNi41Wk0xMiAyMWExLjc1IDEuNzUgMCAxIDAtLjAwMS0zLjUwMUExLjc1IDEuNzUgMCAwIDAgMTIgMjFabTYuMjUtMTQuNWExLjc1IDEuNzUgMCAxIDAtLjAwMS0zLjUwMUExLjc1IDEuNzUgMCAwIDAgMTguMjUgNi41WiIgZmlsbD0iI2ZmZmZmZiIvPjxwYXRoIGQ9Ik02LjUgNy43NXYxQTIuMjUgMi4yNSAwIDAgMCA4Ljc1IDExaDYuNWEyLjI1IDIuMjUgMCAwIDAgMi4yNS0yLjI1di0xSDE5djFhMy43NSAzLjc1IDAgMCAxLTMuNzUgMy43NWgtNi41QTMuNzUgMy43NSAwIDAgMSA1IDguNzV2LTFaIiBmaWxsPSIjZmZmZmZmIi8+PHBhdGggZD0iTTExLjI1IDE2LjI1di01aDEuNXY1aC0xLjVaIiBmaWxsPSIjZmZmZmZmIi8+PC9zdmc+
[forks-url]: https://github.com/Argona7/TgDowloander/network/members
[stars-shield]: https://img.shields.io/github/stars/Argona7/TgDowloander.svg?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNiAxNiIgd2lkdGg9IjE2IiBoZWlnaHQ9IjE2Ij4NCiAgPHBhdGggZD0iTTggLjI1YS43NS43NSAwIDAgMSAuNjczLjQxOGwxLjg4MiAzLjgxNSA0LjIxLjYxMmEuNzUuNzUgMCAwIDEgLjQxNiAxLjI3OWwtMy4wNDYgMi45Ny43MTkgNC4xOTJhLjc1MS43NTEgMCAwIDEtMS4wODguNzkxTDggMTIuMzQ3bC0zLjc2NiAxLjk4YS43NS43NSAwIDAgMS0xLjA4OC0uNzlsLjcyLTQuMTk0TC44MTggNi4zNzRhLjc1Ljc1IDAgMCAxIC40MTYtMS4yOGw0LjIxLS42MTFMNy4zMjcuNjY4QS43NS43NSAwIDAgMSA4IC4yNVptMCAyLjQ0NUw2LjYxNSA1LjVhLjc1Ljc1IDAgMCAxLS41NjQuNDFsLTMuMDk3LjQ1IDIuMjQgMi4xODRhLjc1Ljc1IDAgMCAxIC4yMTYuNjY0bC0uNTI4IDMuMDg0IDIuNzY5LTEuNDU2YS43NS43NSAwIDAgMSAuNjk4IDBsMi43NyAxLjQ1Ni0uNTMtMy4wODRhLjc1Ljc1IDAgMCAxIC4yMTYtLjY2NGwyLjI0LTIuMTgzLTMuMDk2LS40NWEuNzUuNzUgMCAwIDEtLjU2NC0uNDFMOCAyLjY5NFoiIGZpbGw9IiNmZmZmZmYiPjwvcGF0aD4NCjwvc3ZnPg0K
[stars-url]: https://github.com/Argona7/TgDowloander/stargazers
[license-shield]: https://img.shields.io/github/license/Argona7/TgDowloander.svg?style=for-the-badge
[license-url]: https://github.com/Argona7/TgDowloander/blob/main/LICENSE
[telegram-shield]: https://img.shields.io/badge/Telegram-29a9eb?style=for-the-badge&logo=telegram&logoColor=white
[telegram-url]: https://t.me/ArgonaResearch
[product-screenshot]: https://i.ibb.co/DP8mfx9P/image.png
[Python.com]: https://img.shields.io/badge/python%203.11-3670A0?style=for-the-badge&logo=python&logoColor=ffffff
[Python-url]: https://www.python.org/downloads/release/python-3110/

