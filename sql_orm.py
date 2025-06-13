from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, declarative_base
from models import Boga_Bucks, Costs, Track_Roll
from datetime import datetime

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
    
    users = session.query(Boga_Bucks).all()

    if not users:
        return "Nobody has rolled yet!"
    
    curr = 1
    response = "Boga Bucks Leaderboard:\n"
    for user in users:
        response += "{0}. <@{1}>: `{2}`\n".format(curr, user.user_id, user.boga_bucks)
        curr += 1
    
    session.close()

    return response

def generate_user_bull(user_id: int, month=None, year=None):
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