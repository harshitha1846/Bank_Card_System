# importing required modules
import random
import sqlite3


class Bank:
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()

    """ it creates new table if table doesn't exists"""
    cur.execute("""
                CREATE TABLE IF NOT EXISTS card(
                id INTEGER,
                number TEXT,
                pin TEXT,
                balance INTEGER DEFAULT 0
                )
            """)
    conn.commit()
    id = 0

    """ it is the main menu"""

    @staticmethod
    def start():
        while True:
            print('1. Create an account\n2. Log into account\n0. Exit')
            choice = int(input())
            if choice == 1:
                Bank.create()
            elif choice == 2:
                Bank.login()
            elif choice == 0:
                print('Bye!')
                Bank.conn.close()
                break
            else:
                print("Invalid choice")
            print()

    """If the user asks for Balance, you should read the balance of the account from the 
        database and output it into the console."""

    @staticmethod
    def balance(acc):
        bal = Bank.cur.execute(f"SELECT balance FROM card WHERE number = {acc}").fetchone()[0]
        Bank.conn.commit()
        print(f'Balance: {bal}')

    """Add income item should allow us to deposit money to the account."""

    @staticmethod
    def add_income(acc):
        income = int(input('Enter income:\n'))
        Bank.cur.execute(f"""UPDATE card SET balance = balance + {income}
                        WHERE number = {acc}
                        """)
        print('Income was added!')
        Bank.conn.commit()

    """
    Do transfer allows transferring money to another account. We encounter the following errors:

    If the user tries to transfer more money than he/she has, output: "Not enough money!"
    If the user tries to transfer money to the same account, output the following message: “You can't transfer money to the same account!”
    If the receiver's card number doesn’t pass the Luhn algorithm, you should output: “Probably you made mistake in the card number. Please try again!”
    If the receiver's card number doesn’t exist, you should output: “Such a card does not exist.”
    If there is no error, ask the user how much money they want to transfer and make the transaction.
    """

    @staticmethod
    def transfer(acc):
        bal = Bank.cur.execute(f"SELECT balance FROM card WHERE number = {acc}").fetchone()[0]
        Bank.conn.commit()
        print("Transfer")
        transcard = input("Enter card number:\n")
        if acc == transcard:
            print("You can't transfer money to the same account!")
        else:
            validate = Bank.control_no(transcard[:-1])
            if transcard[-1] == validate:
                check = Bank.cur.execute(f"SELECT number FROM card WHERE number = {acc}").fetchone()[0]
                Bank.conn.commit()
                if (check is not None) and transcard[:6] == '400000':
                    money = int(input('Enter how much money you want to transfer:\n'))
                    if money > bal:
                        print("Not enough money!")
                    else:
                        Bank.cur.execute(f"""UPDATE card SET balance = balance + {money}
                                                WHERE number = {transcard}
                                                """)
                        Bank.conn.commit()
                        Bank.cur.execute(f"""UPDATE card SET balance = balance - {money}
                                                                        WHERE number = {acc}
                                                                        """)
                        Bank.conn.commit()
                        print('Success!')
                else:
                    print("Such a card does not exist.")
            else:
                print("Probably you made mistake in the card number. Please try again!")

    """it creates new card"""

    @staticmethod
    def create():
        pin = "%04d" % random.randint(0, 9999)
        account = "%09d" % random.randint(0, 999999999)
        credit = '400000'  + str(account)
        checksum = Bank.control_no(credit)
        card_no = credit + checksum
        bal = 0
        Bank.id += 1
        Bank.cur.execute("INSERT INTO card VALUES (?,?,?,?)", (Bank.id,card_no, pin, bal))
        print('Your card has been created')
        print('Your card number:\n{}\nYour card PIN:\n{}'.format(card_no, pin))
        Bank.conn.commit()

    """it is login method"""

    @staticmethod
    def login():
        print('Enter your card number:')
        card_no = input()
        print('Enter your PIN:')
        pin = input()
        cond = Bank.cur.execute("SELECT number,pin FROM card WHERE number = {} AND pin = {}".format(card_no,pin)).fetchone()
        Bank.conn.commit()
        if cond:
            print('You have successfully logged in!')
            Bank.loginpage(card_no)
        else:
            print("Wrong card number or PIN!")

    """the follow method finds the checksum using luhn algo by finding control no
        it also used to check indirectly whether the given card no is valid or not"""

    @staticmethod
    def control_no(card):
        numbers = list(map(int, card))
        length = len(card)
        for i in range(0,length,2):
            numbers[i] *= 2
        for i in range(0,length,1):
            if numbers[i] > 9:
                numbers[i] -= 9
        total = sum(numbers)
        checksum = (10 - (total % 10)) % 10
        return str(checksum)

    """If the user chooses the Close account item, you should delete that account from the database."""

    @staticmethod
    def close(acc):
        Bank.cur.execute(f"DELETE FROM card WHERE number = {acc}")
        Bank.conn.commit()
        print('The account has been closed!')

    """ It is the menu appear after login into account"""

    @staticmethod
    def loginpage(card):
        while True:
            print('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit')
            choice = int(input())
            if choice == 1:
                Bank.balance(card)
            elif choice == 2:
                Bank.add_income(card)
            elif choice == 3:
                Bank.transfer(card)
            elif choice == 4:
                Bank.close(card)
            elif choice == 5:
                print('You have successfully logged out!')
                break
            elif choice == 0:
                print('Bye!')
                Bank.conn.close()
                exit()


if __name__ == "__main__":
    Bank.start()
