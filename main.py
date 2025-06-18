import discord
from discord.ext import commands
from discord import File
from datetime import datetime, timezone, timedelta, date
import asyncio

import consts
import ask_cmd
import urban_dict
import youtube
import boba_math
import daily_task
import japan_cmd
import uwuify
import gifgenerate
import twitch_random
import weather
import chatgpt_api
import reset_db
import random
import math
import io
import uuid
from cards import Deck
from sql_orm import engine, log_command, apply_roll, get_command_usage, reset_rolls, get_boga_bucks, add_boga_bucks, get_leaderboard, generate_user_bill, generate_statement, apply_wordle_score, reset_wordle
from models import Base

pst = timezone(timedelta(hours=-8))
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

debug_channel = None

@bot.event
async def on_ready():
  
  print("I'm in")
  print(bot.user)

  global start_time
  start_time = datetime.now()

  daily_task.send_daily_msg.start(bot)
  reset_db.reset_db_task.start(bot)

  global debug_channel
  debug_channel = bot.get_channel(consts.DEBUG_CH_ID)
  await debug_channel.send("I am alive")


@bot.command()
async def sync(ctx):
  print("sync command")
  if ctx.author.id == consts.ALEX_ID or ctx.author.id == consts.JAMES_ID:
    await bot.tree.sync()
    await ctx.send('Command tree synced.')
  else:
    await ctx.send('You must be the owner to use this command!')


@bot.command()
async def echo(ctx, *, args):
  if ctx.author.id == consts.ALEX_ID or ctx.author.id == consts.JAMES_ID:
    if ctx.channel.id == consts.DEBUG_CH_ID:
      newctx = bot.get_channel(consts.GENERAL_CH_ID)
      await newctx.send(args)
    else:
      await ctx.send('it broke')

@bot.hybrid_command(name="help", description="a helpful command")
async def help(ctx):
  await ctx.send('ask <@{0}>'.format(consts.ALEX_ID))

@bot.hybrid_command(name="urban", description="define a word")
async def urban(ctx, term: str = commands.parameter(default="", description="type any word or phrase")):
  term = term.strip().lower()
  if len(term) > 0:
    try:
      result = urban_dict.define(term)
      await ctx.send(result)
      log_command("urban")
    except:
      await ctx.send("I don't know what {0} is".format(term))
  else:
    await ctx.send("Please add a phrase")


@bot.hybrid_command(name="randword", description="random urban dictionary word")
async def randword(ctx):
  result = urban_dict.random()
  await ctx.send(result)
  log_command("randword")


@bot.hybrid_command(name="wordoftheday", description="daily word")
async def wordoftheday(ctx):
  result = urban_dict.word_of_the_day()
  await ctx.send(result)
  log_command("wordoftheday")


@bot.hybrid_command(name="meme", description="Watch this video.")
async def meme_video(ctx):
  await ctx.send("https://www.instagram.com/p/Ct_icUhuYn7/")
  log_command("meme")


@bot.hybrid_command(name="japan", description="wack wrapper japan countdown")
async def japan(ctx):
  days, hours, minutes, seconds = japan_cmd.countdown(datetime(2025, 1, 1, tzinfo=pst))
  msg = "{0} days, {1} hours, {2} minutes, {3} seconds till Japan :airplane: :flag_jp:".format(days, hours, minutes, seconds)
  await ctx.send(msg)
  log_command("japan")


@bot.hybrid_command(name="bye-wayne", description="wack wrapper wayne exit countdown")
async def wayne(ctx):
  days, hours, minutes, seconds = japan_cmd.countdown(datetime(2024, 8, 11, tzinfo=pst))
  msg = "{0} days, {1} hours, {2} minutes, {3} seconds till Wayne fricks himself in Misery :student: :pill: ".format(days, hours, minutes, seconds)
  await ctx.send(msg)
  log_command("bye-wayne")


@bot.hybrid_command(name="uptime", description="time when bot started")
async def uptime(ctx):
  global start_time
  diff = datetime.now() - start_time
  days = diff.days
  hours, rem = divmod(diff.seconds, 3600)
  minutes, seconds = divmod(rem, 60)
  diff_str = "{0} days, {1} hours, {2} minutes, {3} seconds".format(days, hours, minutes, seconds)
  await ctx.send("I was started at `{0}`.\nI've been up for `{1}`.".format(start_time, diff_str))
  log_command("uptime")


@bot.hybrid_command(name="ask", description="truthfully answers a question with yes or no")
async def ask(ctx, question: str):
  res = ask_cmd.ask(question)
  await ctx.send(res)
  log_command("ask")


@bot.hybrid_command(name="boba", description="Calculate price based off boba")
async def boba(ctx, value: str):
  res = boba_math.calc(value)
  await ctx.send(res)
  log_command("boba")


@bot.hybrid_command(name="yt-trending", description="#1 trending video on youtube")
async def yt_trending(ctx):
  res = youtube.get_trending()
  msg = "The #1 trending video on youtube is:\n{0}".format(res)
  await ctx.send(msg)
  log_command("yt-trending")


@bot.hybrid_command(name="uwu", description="uwuify sentence given in user response.")
async def uwu(ctx, *, args):
  res = uwuify.uwuify(args)
  await ctx.send(res)
  log_command("uwu")


@bot.hybrid_command(name="twitch-streamer", description="Give you a random streamer currently live on Twitch.")
async def twitch_streamer(ctx):
  res = twitch_random.generate_channel()
  await ctx.send(res)
  log_command("twitch-streamer")


@bot.hybrid_command(name="weather", description="Get the current weather in a specific location.")
async def current_weather(ctx, *, args):
  res, condition, icon, err = weather.get_weather(args)
  if err:
    await ctx.send(res)
    global debug_channel
    await debug_channel.send("Error: {0}".format(err))
  else:
    response = "{0}\nThe weather is currently [**{1}**](https:{2})".format(res, condition.upper(), icon)
    await ctx.send(response)
    log_command("weather")


@bot.hybrid_command(name="image", description="Generate an image based on a prompt. THIS COSTS MONEY.")
async def image(ctx, *, args):
  await ctx.defer()
  response, err = chatgpt_api.gen_image_gpt(ctx.author.id, args)

  if err:
    global debug_channel
    await debug_channel.send("Error: {0}".format(err))
    await ctx.send(response)
    return
  
  random_uuid = uuid.uuid4()
  
  file = discord.File(io.BytesIO(response), filename=str(random_uuid) + ".png")
  await ctx.send(file=file)

  log_command("image")
  


@bot.hybrid_command(name="bill", description="Get the current bill for the user. If no user is specified, it will default to the author.")
async def bill(ctx, user: discord.Member=None, month: int=None, year: int=None): 
  # Gets bill of user from specific month/year if passed by user, else get current month/year. 

  today = datetime.now()
  
  user_id = ctx.author.id if user is None else user.id
  month = today.month if month is None else month
  year = today.year if year is None else year

  if month < 1 or month > 12:
    await ctx.send("Please send a valid date.")
    return

  if year < 2024 or year > today.year:
    await ctx.send("Please send a valid date.")
    return

  response = generate_user_bill(user_id, month, year)
  
  await ctx.send(response)
  log_command("bill")


@bot.hybrid_command(name="usage", description="Check usage of commands of Boga bot so far.")
async def usage(ctx):
  await ctx.defer()
  res = get_command_usage()
  await ctx.send(res)
  log_command("usage")


@bot.hybrid_command(name="goon", description="Enter the gooniverse")
async def goon(ctx):
  await ctx.send("https://tenor.com/view/jarvis-iron-man-goon-gif-5902471035652079804")
  log_command("goon")

@bot.hybrid_command(name="jiawei", description="Where's the japan video Jiawei?")
async def roast_jiawei(ctx):
  japan_return_date = date(2023, 9, 7)
  today = date.today()

  num_days = abs((today - japan_return_date).days)
  log_command("jiawei")
  await ctx.send("It's been about {0} days that <@!{1}> has stalled making the Japan video :JiaweiOOO:".format(num_days, consts.JIAWEI_ID))
  

@bot.hybrid_command(name="roll", description="Roll for Boga Bucks, once a day.")
async def roll(ctx):
  if ctx.author.id == consts.JIAWEI_ID:
    await ctx.send("You cannot roll for Boga Bucks, finish the Japan video first <@!{0}>!!".format(consts.JIAWEI_ID))
    return
  random_number = random.randint(0, 5)
  response = apply_roll(ctx.author.id, random_number)
  await ctx.send(response)
  log_command("roll")

@bot.hybrid_command(name="boga-wallet", description="Check your Boga Bucks balance.")
async def boga_wallet(ctx):
  balance = get_boga_bucks(ctx.author.id)
  await ctx.send("You have {0} Boga Bucks!".format(balance))
  log_command("boga-wallet")

@bot.hybrid_command(name="boga-board", description="Top boga buck farmers.")
async def boga_board(ctx):
  response = get_leaderboard()
  await ctx.send(response, allowed_mentions=discord.AllowedMentions.none())
  log_command("boga-board")

def is_boga_bot_chat():
    async def predicate(ctx):
        if ctx.channel.id != consts.BOGA_BOT_CHANNEL_ID:
            await ctx.send("This command can only be used in the designated channel.")
        return ctx.channel.id == consts.BOGA_BOT_CHANNEL_ID
    return commands.check(predicate)

@bot.hybrid_command(name="ride-the-bus", description="Ride the bus. Bet your Boga Bucks.")
@is_boga_bot_chat()
async def ride_the_bus(ctx, bet: int):
  # Start a game of ride. 2x red or black. 3x higher or lower. 4x inside or outside. 20x suit.
  # after red or black, keep previous card's value to compare for higher or lower.
  # keep last 2 values to compare for inside or outside. this is where we check if next card pulled is inside the values of 2 prev or not. 
  # lastly guess the suit to get 20x. independent of previous cards. 

  # Before we do anything though, check if bet is within bounds.
  if ctx.author.id == consts.JIAWEI_ID:
    await ctx.send("You cannot bet for Boga Bucks, finish the Japan video first <@!{0}>!!".format(consts.JIAWEI_ID))
    return

  bet = math.ceil(bet) 
  balance = get_boga_bucks(ctx.author.id)
  if bet < 1 or bet > balance:
    await ctx.send("You do not have enough to bet that much. You have {0} Boga Bucks.".format(balance))
    return
  
  rounds = [
    "Pick a color: red or black, react to this message with :red_circle: or :black_circle:.",
    "Pick a value: higher or lower, react to this message with :arrow_up: or :arrow_down:.",
    "Pick a position: inside or outside, react to this message with :inbox_tray: or :outbox_tray:.",
    "Guess the suit: hearts, diamonds, clubs, or spades, react to this message with :heart: or :diamonds: or :clubs: or :spades:."
  ]

  multipliers = [2, 3, 4, 20]

  winnings = 0 # if this is 0 at end, subtract bet from balance. 
  deck = Deck()
  rounds_idx = 0

  reactions = [ ["🔴", "⚫"] ,  ["⬆️", "⬇️"],  ["📥", "📤"],  ["♥️", "♦️", "♣️", "♠️"]]
  cards_pulled = []

  color_match = {"🔴": ["hearts", "diamonds"], "⚫": ["clubs", "spades"]}
  
  face_values = {"J": 11, "Q": 12, "K": 13, "A": 14} # not sure how this works for Ace yet, probably need to do both ranges...?

  suit_match = {"hearts": "♥️", "diamonds": "♦️", "clubs": "♣️", "spades": "♠️"}

  add_boga_bucks(ctx.author.id, -bet) # subtract bet from balance.

  messages = []
  
  while winnings >= 0 and rounds_idx < len(rounds):
    curr_card = deck.pull_card()

    curr_msg = "<@!{0}>\n".format(ctx.author.id)
    curr_msg += rounds[rounds_idx]
    if rounds_idx > 0:
      curr_msg += "\nPrevious cards: "
      for card in cards_pulled:
        curr_msg += "{0}, ".format(card.get_card())
      curr_msg = curr_msg[:-2]
      curr_msg += "\nYou can stop betting here by reacting with :octagonal_sign: to take your winnings, or try and bet for more!"
      curr_msg += "\nYou have {0} won so far!".format(winnings)
    
    message = await ctx.send(curr_msg)
    messages.append(message)

    for reaction in reactions[rounds_idx]:
      await message.add_reaction(reaction)
    
    if rounds_idx > 0:
      await message.add_reaction("🛑")

    try:
      reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=lambda r, user: user == ctx.author and r.message.id == message.id and r.emoji in (reactions[rounds_idx] + ["🛑"]))
      
      if str(reaction.emoji) == "🛑" and rounds_idx > 0:
        new_msg = await ctx.send("You stopped betting. You won {0} Boga Bucks!".format(winnings))
        messages.append(new_msg)
        break
      
      round_win = False
      if str(reaction.emoji) in reactions[rounds_idx]:
        # continue betting. 
        if rounds_idx == 0: # red or black. 
          if curr_card.get_suit() in color_match[str(reaction.emoji)]:
            round_win = True
          else:
            round_win = False
            
        # second round.
        elif rounds_idx == 1:

          while curr_card.get_value() == cards_pulled[0].get_value(): # in case of same value, just keep repulling card. 
            new_card = deck.pull_card()
            deck.add_card(curr_card)
            curr_card = new_card

          card_1, card_2 = cards_pulled[0].get_value(), curr_card.get_value()
          
          if card_1 in face_values:
            card_1 = face_values[card_1]
          if card_2 in face_values:
            card_2 = face_values[card_2]
          
          card_1 = int(card_1)
          card_2 = int(card_2)

          if card_1 < card_2 and str(reaction.emoji) == "⬆️":
            round_win = True
          elif card_1 > card_2 and str(reaction.emoji) == "⬇️":
            round_win = True
          else:
            round_win = False
       
        # third round. 
        elif rounds_idx == 2:  # need to keep repulling card if the value is same. 
          card_1, card_2 = cards_pulled[0].get_value(), cards_pulled[1].get_value()
          card_3 = curr_card.get_value()
          
          if card_1 in face_values:
            card_1 = face_values[card_1]
          if card_2 in face_values:
            card_2 = face_values[card_2]
          if card_3 in face_values:
            card_3 = face_values[card_3]
          
          card_1 = int(card_1)
          card_2 = int(card_2)
          card_3 = int(card_3)

          card_range = range(min(card_1, card_2) + 1, max(card_1, card_2))
          
          if str(reaction.emoji) == "📥" and card_3 in card_range:
            round_win = True
          elif str(reaction.emoji) == "📤" and card_3 not in card_range:
            round_win = True
          else:
            round_win = False

        # fourth round. 
        elif rounds_idx == 3:
          suit = curr_card.get_suit()

          if suit_match[suit] == str(reaction.emoji):
            round_win = True
          else:
            round_win = False
        
        curr_msg = ""
        if round_win:
          winnings = bet * multipliers[rounds_idx]
          curr_msg += "You guessed correctly! It was {0} of {1}!\n".format(curr_card.get_value(), suit_match[curr_card.get_suit()])
          curr_msg += "You have won {0} Boga Bucks!".format(winnings)
          rounds_idx += 1
        else:
          winnings = 0
          curr_msg += "You guessed incorrectly! It was {0} of {1}!\n".format(curr_card.get_value(), suit_match[curr_card.get_suit()])
          curr_msg += "You have lost {0} Boga Bucks!".format(bet)
        
        new_msg = await ctx.send(curr_msg)
        messages.append(new_msg)

        cards_pulled.append(curr_card)

        if not round_win:
          break

    except asyncio.TimeoutError:
      winnings = 0
      new_msg = await ctx.send("You took too long to respond. Game over. You lost {0} Boga Bucks.".format(bet))
      messages.append(new_msg)
      break
  
  add_boga_bucks(ctx.author.id, winnings)
  await ctx.send("<@!{0}>\n You finished gambling! You now have {1} Boga Bucks.".format(ctx.author.id, get_boga_bucks(ctx.author.id)))

  await asyncio.sleep(20)
  for msg in messages:
    message_id = msg.id
    to_delete = await ctx.fetch_message(message_id)
    await to_delete.delete()
    
  log_command("ride-the-bus")

@bot.hybrid_command(name="features", description="Request a feature for the bot.")
async def features(ctx):
  await ctx.send("Check https://github.com/jycor/boga_bot/issues for feature requests. You can also ping Alex.")
  log_command("features")

@bot.hybrid_command(name="laugh", description="Minion laugh.")
async def laugh(ctx):
  await ctx.send("https://tenor.com/view/minion-minion-laughing-minion-popcorn-wriogifs-gif-10648794811524455015")
  log_command("laugh")

@bot.hybrid_command(name="blaugh", description="Minion laugh 4K 1440P.")
async def blaugh(ctx):
  await ctx.send("https://tenor.com/view/bahaha-lol-hd-gif-minion-minion-laugh-gif-2154867417577880306")
  log_command("blaugh")

@bot.event
async def on_message(message):
  
  
  if message.author.bot:
    if message.type == discord.MessageType.chat_input_command and message.author.name == "Wordle":
      user_id = message.interaction_metadata.user.id
      ctx = await bot.get_context(message)

      # Wordle message could be either before or after user completes the game. 
      wordle_content = message.components[0].children[0].content.split("\n")[0]
      wordle_score = wordle_content.split(" ")[-1][0] # get the last word in the string, which is the score.
      
      if wordle_score == "X": # if the user did not complete the game, do not give them any score.
        wordle_score = 7
      boga_bucks_earned = 7 - int(wordle_score)
      response = apply_wordle_score(user_id, boga_bucks_earned) # apply the score to the user.

      await ctx.send("<@!{0}>. {1}".format(user_id, response))
      return
  
  else:
    return
  
  # possible text commands
  cmd = message.content.split(" ")[0]
  match cmd:
    case "/sync":
      ctx = await bot.get_context(message)
      await sync(ctx)
      return
    case "/echo":
      ctx = await bot.get_context(message)
      await echo(ctx, args=message.content[6:])
      return
    case "/randgif": # Leave in case of integration testing. Won't make as hybrid command cause just used for daily announcement. 
      ctx = await bot.get_context(message)
      gif = gifgenerate.generate_gif()
      if gif:
        await message.channel.send(gif)
      else:
        await message.channel.send("Gif failed.")
      return
    case "/forget":
      ctx = await bot.get_context(message)
      if ctx.author.id == consts.ALEX_ID or ctx.author.id == consts.JAMES_ID:
        chatgpt_api.clear_history()
        await message.channel.send("Cleared chat history.")
      return
    case "/statement":
      response = generate_statement()
      await message.channel.send(response)
      return
    case "/reset": # in case daily task fails to run. 
      ctx = await bot.get_context(message)
      if ctx.author.id == consts.ALEX_ID or ctx.author.id == consts.JAMES_ID:
        reset_rolls()
        await message.channel.send("Reset time, everyone can reroll again!")
      return
  
  if message.content == "https://tenor.com/view/minion-minion-laughing-minion-popcorn-wriogifs-gif-10648794811524455015":
    await message.channel.send("https://tenor.com/view/minion-minion-laughing-minion-popcorn-wriogifs-gif-10648794811524455015")
    return

  if message.content == "https://tenor.com/view/bahaha-lol-hd-gif-minion-minion-laugh-gif-2154867417577880306":
    await message.channel.send("https://tenor.com/view/bahaha-lol-hd-gif-minion-minion-laugh-gif-2154867417577880306")
    return
  
  # ignore messages that don't mention the bot
  if not bot.user.mentioned_in(message):
    return

  if message.author.id == consts.JIAWEI_ID: # Jiawei roast message if he tries to mention the bot. 
    await message.channel.send("Please finish the Japan video <@!{0}>".format(consts.JIAWEI_ID))
    return

  ctx = await bot.get_context(message)  
  async with ctx.typing():
    response, err = await chatgpt_api.generate_chatgpt_response(message.author.id, message.content)
    if err:
      global debug_channel
      await debug_channel.send("Error: {0}".format(err))
    
  for i in range(0, len(response), chatgpt_api.DISCORD_MSG_LIMIT):
    async with ctx.typing():
      await message.channel.send(response[i:i+chatgpt_api.DISCORD_MSG_LIMIT], reference=message)
      await asyncio.sleep(0.5) # delay to make it feel more natural; can remove
  
  log_command("chatgpt")
  
Base.metadata.create_all(engine) # essentially creates new tables if they do not exist. 
bot.run(consts.API_KEY)
