from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base
from models import Boga_Bucks, Costs, Track_Roll, Usage
from datetime import datetime

PROG_CHR = "*"
MISS_CHR = "-"

Base = declarative_base()

engine = create_engine("sqlite:///boga.db")  # echo=True for debugging

Session = sessionmaker(bind=engine)

# Track costs for /statement and /bill
def log_cost(user_id: int, type: str, cost: float):
    session = Session()
    new_cost = Costs(user_id=user_id, date=datetime.now(), type=type, cost=cost)
    session.add(new_cost)
    session.commit()
    session.close()

def apply_roll(user_id: int, roll: int):
    session = Session()

    curr_user = session.query(Track_Roll).filter(Track_Roll.user_id == user_id).first()
    
    return_message = ""
    # curr_user is None if the user hasn't rolled yet.
    if not curr_user:
        new_user = Boga_Bucks(user_id=user_id, boga_bucks=roll)
        session.add(new_user)
        session.commit()
        
        new_roll = Track_Roll(user_id=user_id, roll=1, streak=0)
        session.add(new_roll)
        session.commit()
        return_message = "You earned `{}` Boga Bucks!".format(roll)

    else:
        if curr_user.roll == 1: # User exists, has previously rolled today. 
            return_message = "You already rolled today. Try again after reset! (12:00am PST)"
        else: # User exists, but didn't roll today. 
            curr_user.roll = 1
            session.commit()

            user_bucks = session.query(Boga_Bucks).filter(Boga_Bucks.user_id == user_id).first()
            user_bucks.boga_bucks += roll
            session.commit()

            return_message = "You earned `{}` Boga Bucks!".format(roll)
        
    session.close()
    return return_message

def reset_rolls():
    session = Session()

    for user in session.query(Track_Roll).filter(Track_Roll.roll == 1):
        user.streak += 1
    session.commit()

    session.query(Track_Roll).filter(Track_Roll.roll == 0).update({Track_Roll.streak: 0})
    session.commit()

    session.query(Track_Roll).update({Track_Roll.roll: 0})
    session.commit()

    session.close()

def get_boga_bucks(user_id: int):
    session = Session()

    user_bucks = session.query(Boga_Bucks).filter(Boga_Bucks.user_id == user_id).first()
    
    to_return = user_bucks.boga_bucks
    session.commit()
    session.close()
    
    return to_return

def add_boga_bucks(user_id: int, amount: int):
    session = Session()
    user_bucks = session.query(Boga_Bucks).filter(Boga_Bucks.user_id == user_id).first()
    user_bucks.boga_bucks += amount

    session.commit()
    session.close()

def get_leaderboard():
    session = Session()
    
    users = session.query(Boga_Bucks).order_by(Boga_Bucks.boga_bucks.desc()).all()

    if not users:
        return "Nobody has rolled yet!"
    
    curr = 1
    response = "Boga Bucks Leaderboard:\n"
    for user in users:
        response += "{0}. <@{1}>: `{2}`\n".format(curr, user.user_id, user.boga_bucks)
        curr += 1
    
    session.close()

    return response

def generate_user_bill(user_id: int, month=None, year=None):
    session = Session()

    start_date = datetime(year=year, month=month, day=1)
    end_month = month + 1 if month != 12 else 1
    end_year = year + 1 if end_month == 1 else year
    end_date = datetime(year=end_year, month=end_month, day=1)

    bill = session.query(func.sum(Costs.cost)).filter(
        Costs.user_id == user_id, 
        Costs.date >= start_date, 
        Costs.date <= end_date
    ).first()

    if not bill:
        return "You owe 0 dollars!"

    total_cost = bill[0]
    
    session.close()

    return "<@!{}> owes `${}` for `{}/{}`".format(user_id, total_cost, month, year)

def generate_statement():
    session = Session()

    results = (
        session.query(
            Costs.user_id,
            func.sum(Costs.cost).label('total_cost')
        )
        .group_by(Costs.user_id)
        .order_by(
            func.sum(Costs.cost).desc(),
            Costs.user_id
        )
        .all()
    )

    if len(results) == 0:
        return "Nobody has used the bot yet"

    res = "# Statement Summary starting from 04/2024\n\n"

    total = 0
    for row in results:
        tmp = "<@!{}> owes `${}`\n".format(row[0], row[1])
        res += tmp
        total += row[1]
    
    res += "\nTotal: `${}`".format(total)

    session.close()

    return res

def log_command(command: str):
    session = Session()

    command_count = session.query(Usage).filter(Usage.command == command).first()

    if not command_count:
        new_usage = Usage(command=command, count=0)
        session.add(new_usage)
        session.commit()

    command = session.query(Usage).filter(Usage.command == command).first()

    command.count += 1

    session.commit()
    session.close()

def get_command_usage():
    session = Session()

    commands = session.query(Usage).order_by(Usage.count.desc(), Usage.command.asc()).all()
    
    total = session.query(func.sum(Usage.count)).scalar()
    
    res = "```"

    for row in commands:
        
        percent = round((row.count / total) * 100, 2)
        progress = round((row.count / total) * 10)
        progress_bar = (PROG_CHR * progress) + (MISS_CHR * (10 - progress))

        res += "/{:15} [{}] {}%\n".format(row.command, progress_bar, str(percent))
    
    res += "```"

    return res