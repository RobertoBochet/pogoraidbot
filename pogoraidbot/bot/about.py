from telegram.utils.helpers import escape_markdown

import pogoraidbot

MESSAGE = """
Hi, i am an instance of [PoGoRaidBot](https://github.com/RobertoBochet/pogoraidbot), a *self\-hostable Telegram bot* with the aim of helping Pokémon GO group to organize raids\.

My source code is completely *open* and you can find it on [GitHub](https://github.com/RobertoBochet/pogoraidbot) \(__pull requests are highly appreciated__\)\. 

_It is really simple to create a new instance of me for your own group of Pokémon GO, you can find the instruction to do it into git repository\._

I am at version *{version}*
""".format(version=escape_markdown(pogoraidbot.__version__, version=2))
