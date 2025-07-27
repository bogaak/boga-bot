from discord.ext import tasks
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, time
from consts import JIAWEI_ID

import consts
import youtube
import urban_dict
import gifgenerate
import weather
import asyncio

pst = ZoneInfo(key='America/Los_Angeles')
daily_msg_time = time(hour=8, tzinfo=pst)

DISCORD_MSG_LIMIT = 2000

# USE THIS FOR TESTING
# dt = datetime.now() + timedelta(seconds=10)
# daily_msg_time = time(hour=dt.hour, minute=dt.minute, second=dt.second, tzinfo=pst)

# ANOTHER DEBUG METHOD IN CASE ABOVE NOT WORKING: 
# @tasks.loop(seconds=5.0)

@tasks.loop(time=daily_msg_time)
async def send_daily_msg(bot):
  ctx = bot.get_channel(consts.DEBUG_CH_ID)

  urban_dict.reset_word_of_the_day()

  greeting = "Good morning everyone!"
  daily_word_msg = "The Word of the Day is:\n{0}".format(urban_dict.word_of_the_day())
  daily_yt_vid = "The #1 trending video on YouTube is:\n{0}".format(youtube.get_trending())
  res, condition, _, err = weather.get_weather("Chino")
  daily_weather = "{0} Currently it is {1}.".format(res, condition)
  j_res, j_condition, _, j_err = weather.get_weather("Los Angeles")
  daily_james_weather = "For James, {0} Currently it is {1} :) .".format(j_res, j_condition)
  jiawei_roast = "<@!{0}>, for the love of god, please finish the fucking Japan video.".format(JIAWEI_ID)
  msg = "{0}\n{1}\n{2}\n{3}\n{4}\n\n\n{5}".format(greeting, daily_word_msg, daily_yt_vid, daily_weather, daily_james_weather, jiawei_roast)
  gif_url = gifgenerate.generate_gif()

  for i in range(0, len(msg), DISCORD_MSG_LIMIT):
    
    await ctx.send(msg[i:i+DISCORD_MSG_LIMIT])
    await asyncio.sleep(0.5) # delay to make it feel more natural; can remove
  
  await ctx.send(gif_url)

  if not err and not j_err:
    return
  
  debug_channel = bot.get_channel(consts.DEBUG_CH_ID)
  if err:
    await debug_channel.send("Error: {0}".format(err))
  if j_err:
    await debug_channel.send("Error: {0}".format(j_err))