Usage

```
git clone https://github.com/snowskeleton/atomic-empire-cli.git
cd atomic-empire-cli

python -m venv .venv
source .venv/bin/activate
pip install .

alembic upgrade head

empire login

empire deck add --name "Deck name"
    <paste your deck in Arena format when prompted>

empire deck purchase -n "Deck name"
```
