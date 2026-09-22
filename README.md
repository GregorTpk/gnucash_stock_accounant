Command line tool for writing csv data exported from Trade Republic into gnucash.

# Dependencies

Requires `piecash` as non-builtin library. Can be installed via `pip3 install piecash`.

# Usage

First, create a config json file containing information about the gnucash database, brokers and ETFs. For details, see the subsection **Config File**.

Basic usage:

`python3 gnucash_stock_accountant.py [--no-backup] config-json broker-name transactions-csv`

* `config-json`: Full path to the config json file
* `broker-name`: Used broker as defined in the given config file.
* `transactions-csv`: Full path to a csv file exported from the broker including **only new** transactions.
* `--no-backup`: Per default, the script creates a backup of the gnucash database. The flag deactivates this behaviour.

**Important note**: Currently, there is no check whether a transaction already exists in gnucash. Everything from the csv file is written to the gnucash database. Therefore, multiple csv exports must use non-overlapping time frames.

## Config File

Attributes of the json file:

* `database`: Full path to the gnucash database.
* `brokers`: List containing a dictionary per used broker.
    * `name`: Descriptor of the broker.
    * `cash_acct_fullname`: The full name of the cash account in gnucash, separated by `:`.
    * `fee_acct_fullname`: The full name of the account for transactions fees in gnucash, separated by `:`.
    * `transact_buy_descr`: Format string for buying a stock. Available variables for formatting: `display_name`.
    * `transact_sell_descr`: Format string for selling a stock. Available variables for formatting: `display_name`.
    * `transact_savings_plan_descr`: Format string when executing a savings plan. Available variables for formatting: `display_name`.
    * `etfs`: List containing traded ETFs.
        * `display_name`: The display name provided to the description of the transaction.
        * `symbol`: ISIN of the ETF. Used as the identifier in the csv file.
        * `etf_acct_fullname`: The full name of the stock account in gnucash, separated by `:`.

Example:

    {
        "database": "/home/user/Documents/GnuCash/my_gnucash_database.gnucash",
        "brokers": [
            {
                "name": "Trade Republic",
                "cash_acct_fullname": "Aktiva:Barvermögen:Trade Republic",
                "fee_acct_fullname": "Aufwendungen:Sonstiges:Bankgebühren:Transaktionsgebühren",
                "transact_buy_descr": "Investment ({display_name})",
                "transact_sell_descr": "Verkauf ({display_name})",
                "transact_savings_plan_descr": "ETF Sparplan {display_name}",
                "etfs": [
                    {
                        "display_name": "MSCI Emerging Markets",
                        "symbol": "LU1681045370",
                        "etf_acct_fullname": "Aktiva:Kapitalanlagen:Trade Republic ETFs:Amundi MSCI Emerging Markets"
                    },
                    {
                        "display_name": "DAX",
                        "symbol": "LU0274211480",
                        "etf_acct_fullname": "Aktiva:Kapitalanlagen:Trade Republic ETFs:Xtrackers DAX"
                    },
                    {
                        "display_name": "MSCI World",
                        "symbol": "IE000BI8OT95",
                        "etf_acct_fullname": "Aktiva:Kapitalanlagen:Trade Republic ETFs:Amundi MSCI World"
                    }
                ]
            }
        ]
    }
