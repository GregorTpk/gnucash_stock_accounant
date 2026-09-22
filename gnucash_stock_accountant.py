from decimal import Decimal
import shutil, argparse, csv, json
from piecash import open_book, Transaction, Split
import datetime

CFG_DATABASE = "database"
CFG_BROKERS = "brokers"
CFG_BROKERS_NAME = "name"
CFG_BROKERS_CASH_ACCT_FULLNAME = "cash_acct_fullname"
CFG_BROKERS_FEE_ACCT_FULLNAME = "fee_acct_fullname"
CFG_BROKERS_ETFS = "etfs"
CFG_ETF_DISPLAY_NAME = "display_name"
CFG_ETF_SYMBOL = "symbol"
CFG_ETF_ETF_ACCT_FULLNAME = "etf_acct_fullname"
CFG_ETF_TRANSACT_BUY_DESCR = "transact_buy_descr"
CFG_ETF_TRANSACT_SELL_DESCR = "transact_sell_descr"
CFG_ETF_TRANSACT_SAVINGS_PLAN_DESCR = "transact_savings_plan_descr"


def update_gnucash_db(db_config_path, broker_name, transactions_csv_path, create_backup=True):
    print("Loading config file...")
    with open(db_config_path) as config_f:
        db_config = json.load(config_f)
        broker_list = db_config[CFG_BROKERS]
        has_found_broker = False
        for br in broker_list:
            if br[CFG_BROKERS_NAME] == broker_name:
                has_found_broker = True

                # Create backup of database
                if create_backup:
                    print("Creating backup...")
                    shutil.copyfile(db_config[CFG_DATABASE], db_config[CFG_DATABASE] + ".backup-" + str(datetime.datetime.now()))
                else:
                    print("Not creating a backup.")

                print("Opening database...")
                with open_book(db_config[CFG_DATABASE], readonly=False, open_if_lock=False) as book:
                    cash_acct = book.accounts(fullname=br[CFG_BROKERS_CASH_ACCT_FULLNAME])
                    fee_acct = book.accounts(fullname=br[CFG_BROKERS_FEE_ACCT_FULLNAME])
                    etf_list = br[CFG_BROKERS_ETFS]
                    with open(transactions_csv_path) as transactions_f:
                        csv_reader = csv.DictReader(transactions_f)
                        print("Processing transactions...")
                        for row in csv_reader:
                            if row["category"] == "TRADING" and row["asset_class"] == "FUND":
                                has_found_etf = False

                                for etf in etf_list:
                                    if etf[CFG_ETF_SYMBOL] == row["symbol"]:
                                        has_found_etf = True

                                        etf_acct = book.accounts(fullname=etf[CFG_ETF_ETF_ACCT_FULLNAME])

                                        enter_date = datetime.datetime.strptime(row["datetime"], "%Y-%m-%dT%H:%M:%S.%fZ")
                                        post_date = datetime.datetime.strptime(row["date"], "%Y-%m-%d").date()

                                        amount = Decimal(row["amount"])
                                        quantity = Decimal(row["shares"])

                                        if row["fee"] == "":
                                            fee = Decimal(0)
                                        else:
                                            fee = Decimal(row["fee"])

                                        if row["type"] == "BUY" and (row["description"].startswith("Savings plan execution")): # Condition hard-coded for trade republic!
                                            descr = br[CFG_ETF_TRANSACT_SAVINGS_PLAN_DESCR]
                                        elif row["type"] == "BUY":
                                            descr = br[CFG_ETF_TRANSACT_BUY_DESCR]
                                        elif row["type"] == "SELL":
                                            descr = br[CFG_ETF_TRANSACT_SELL_DESCR]
                                        else:
                                            descr = f"Transaction ({etf[CFG_ETF_DISPLAY_NAME]})"
                                        descr = descr.format(display_name=etf[CFG_ETF_DISPLAY_NAME])

                                        splits = [
                                                Split(account=cash_acct, value=amount-abs(fee)),
                                                Split(account=etf_acct, value=-amount, quantity=quantity)
                                            ]
                                        if fee != 0:
                                            splits.append(Split(account=fee_acct, value=abs(fee)))

                                        Transaction(
                                            currency=book.default_currency,
                                            description=descr,
                                            enter_date=enter_date,
                                            post_date=post_date,
                                            splits=splits
                                        )
                                if not has_found_etf:
                                    print(f"Warning: Found transactions concerning an unknown etf '{row["symbol"]}':")
                                    print(row)
                    book.save()
        if not has_found_broker:
            print(f"Warning: Did not find given broker '{broker_name}'")
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('config-json', help="Path to the config json file")
    parser.add_argument('broker-name', help="Name of the broker defined in the config json file")
    parser.add_argument('transactions-csv', help="Path to the csv containing new transactions")
    parser.add_argument('--no-backup', action='store_true', default=False, help="Do not create a backup of the gnucash-database")
    args = parser.parse_args()

    config_json = getattr(args, 'config-json')
    broker_name = getattr(args, 'broker-name')
    transactions_csv = getattr(args, 'transactions-csv')

    update_gnucash_db(config_json, broker_name, transactions_csv, create_backup=(not args.no_backup))

