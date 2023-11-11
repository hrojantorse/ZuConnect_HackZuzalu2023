from typing import List, Tuple, cast

import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
import time
import datetime
import pytz

import json

from apscheduler.schedulers.asyncio import AsyncIOScheduler


# Start the scheduler
sched = AsyncIOScheduler()
sched.start()

data_dict = {}

with open("users.json", "r") as in_file:
	data_dict = json.load(in_file) 

def save_to_dict(user, data_key, data_value):

	if not data_dict.get(str(user.id)):
		data_dict[str(user.id)] = {}

	data_dict[str(user.id)][data_key] = data_value	

	with open("users.json", "w") as outfile:
		json.dump(data_dict, outfile)



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

	user = update.effective_user

	keyboard = [
        [
            InlineKeyboardButton("I want to take part in a trial!", callback_data="take_part_in_trial"),
        ],
		[
            InlineKeyboardButton("What is Zutrials?", url='https://docs.google.com/document/d/1BukyGcbP1SYkekHiop6-7bbpAvRGYvcIPV6b0OLqW8U/edit'),
		]
    ]

	reply_markup = InlineKeyboardMarkup(keyboard)

	save_to_dict(user, "username", user.username)
	save_to_dict(user, "first_name", user.first_name)
	save_to_dict(user, "last_name", user.last_name)

	await update.message.reply_text(f'Welcome to the Clinical Trial Bot', reply_markup=reply_markup)

async def remind_fast(data):

	update, num = data

	if num == 0:
		await update.effective_chat.send_message(
			f'Just a reminder that your FAST begins in 15  minutes. \nNo food or beverage EXCEPT WATER',
		)
	if num == 1:
		await update.effective_chat.send_message(
			f'Just a reminder that your FAST begins in 15  minutes. \nNo food or beverage EXCEPT WATER',
		)


async def remind_eat(data):
	update, num = data

	if num == 0:
		keyboard = [
			[
				InlineKeyboardButton("Confirm Reading", callback_data="baseline_reading_confirmed"),
			],
            [
				InlineKeyboardButton("Edit Reading", callback_data="no_device_ready_to_go"),
			],
		]

		reply_markup = InlineKeyboardMarkup(keyboard)

		await update.effective_chat.send_message(
			f'Your fast is over. It is TIME TO EAT:)\n\n PLEASE ENTER YOUR BASELINE GLUCOSE READING. (If your reading is 5.3, then type 5.3)',
			reply_markup=reply_markup
		)
	if num == 1:
		keyboard = [
			[
				InlineKeyboardButton("I have a device ready to go", callback_data="device_ready_to_go"),
			],
            [
				InlineKeyboardButton("I don't have a device", callback_data="no_device_ready_to_go"),
			],
		]

		reply_markup = InlineKeyboardMarkup(keyboard)

		await update.effective_chat.send_message(
			f'Selected {num}',
			reply_markup=reply_markup
		)

async def remind_update(data):
	update, num = data

	if num == 0:
		await update.effective_chat.send_message(
			f'Selected {num}',
		)
	if num == 1:
		await update.effective_chat.send_message(
			f'Selected {num}',
		)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

	query = update.callback_query
	await query.answer()

	user = update.effective_user
	
	if(query.data == "take_part_in_trial"):
		keyboard = [
			[
				InlineKeyboardButton("Glucose Monitor Trial", callback_data="glucose_monitor_trial"),
			],
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		await update.effective_chat.send_message(
			f'Please choose from following available trials',
			reply_markup=reply_markup
		)
	
	if(query.data == "glucose_monitor_trial"):
		keyboard = [
			[
				InlineKeyboardButton("I have a device ready to go", callback_data="device_ready_to_go"),
			],
            [
				InlineKeyboardButton("I don't have a device", callback_data="no_device_ready_to_go"),
			],
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		await update.effective_chat.send_message(
			f'The Glucose trial will help gather data on the response certain variables have on your blood sugar. This way we can find out which help control your blood sugar 🙂\n To get started, you need to have a GCM device attached and activated. Please give it 24 hours after insertion for best accuracy.',
			reply_markup=reply_markup
		)
	if(query.data == "device_ready_to_go"):
		keyboard = [
			[
				InlineKeyboardButton("Check Eligibility", callback_data="check_eligibility"),
			],
            
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		save_to_dict(user, "has_device", True)

		await update.effective_chat.send_message(
			f'Excellent! \n\n Lets check your eligibility before we go ahead',
			reply_markup=reply_markup
		)
	if(query.data == "no_device_ready_to_go"):
		keyboard = [
			[
				InlineKeyboardButton("Back to Main Menu", callback_data="take_part_in_trial"),
			],
            
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		save_to_dict(user, "has_device", False)

		await update.effective_chat.send_message(
			f'Make sure to message @bharat_desci on Telegram to get your device. Start the trial once you get the device. ',
			reply_markup=reply_markup
		)   
		    
	if(query.data == "check_eligibility"):
		keyboard = [
			[
				InlineKeyboardButton("No", callback_data="not_eligible"),
			],
			[
				InlineKeyboardButton("Yes", callback_data="to_exclusion_criteria"),
			],
            
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		await update.effective_chat.send_message(
			f'Are you between the ages of 18 & 50',
			reply_markup=reply_markup
		)

	if(query.data == "not_eligible"):
		save_to_dict(user, "is_eligible", False)

		await update.effective_chat.send_message(
			f'Unfortunately, you will not be eligible to take part in this trial. \n\n Thank you for your interest in Science :)',
		)
		
	if(query.data == "to_exclusion_criteria"):
		keyboard = [
			[
				InlineKeyboardButton("No", callback_data="exclusion_criteria_two"),
			],
			[
				InlineKeyboardButton("Yes", callback_data="not_eligible"),
			],
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		save_to_dict(user, "age_between_18_and_50", True)

		await update.effective_chat.send_message(
			f'Do you have any history of metabolic disorder, including, but not limited to diabetes',
			reply_markup=reply_markup
		)
	if(query.data == "exclusion_criteria_two"):
		keyboard = [
			[
				InlineKeyboardButton("No", callback_data="exclusion_criteria_three"),
			],
			[
				InlineKeyboardButton("Yes", callback_data="not_eligible"),
			],
            
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		save_to_dict(user, "has_metabolic_disorder", False)

		await update.effective_chat.send_message(
			f'Do you take any medication known to effect your blood sugars?',
			reply_markup=reply_markup
		)
	if(query.data == "exclusion_criteria_three"):
		keyboard = [
			[
				InlineKeyboardButton("No", callback_data="good_to_go"),
			],
			[
				InlineKeyboardButton("Yes", callback_data="not_eligible"),
			],
            
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		save_to_dict(user, "takes_blood_sugar_medication", False)

		await update.effective_chat.send_message(
			f'Are you pregnant or currently lactating?',
			reply_markup=reply_markup
		)
	if(query.data == "good_to_go"):
		keyboard = [
			[
				InlineKeyboardButton("I consent", callback_data="consent_confirmed"),
			],
			[
				InlineKeyboardButton("It's not for me", callback_data="not_interested"),
			],
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		
        ## I need to add the URL for the consent form here

		save_to_dict(user, "is_pregnant", False)

		await update.effective_chat.send_message(
			f'Looks like you are all set. Before we begin the trial, make sure to read the study explainer. Take your time as it includes information on potential adverse effects.',
			reply_markup=reply_markup
		)

	if(query.data == "not_interested"):
		save_to_dict(user, "isInterested", False)

		await update.effective_chat.send_message(
			f'We hope you change your mind! \n\n Thank you for your interest in Science :)',
		)

## How do we set the time as a variable which gets recorded by the system too
	if(query.data == "consent_confirmed"):
		keyboard = [
			[
				InlineKeyboardButton("9:00am", callback_data="time_selected_0"),
			],
			[
				InlineKeyboardButton("12:00pm", callback_data="time_selected_1"),
			],
            [
				InlineKeyboardButton("3:00pm", callback_data="time_selected_2"),
			],
			[
				InlineKeyboardButton("6:00pm", callback_data="time_selected_3"),
			],
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	

		save_to_dict(user, "isInterested", True)

		await update.effective_chat.send_message(
			f'You need to select a time of the day that is convenient for you. You have to have fasted for 3 hours before this time and then need to fast for a further 90 min after.\n\n\n INSTRUCTIONS: You will where you have a certain type of food on: Day 1 and then the same food on Day 2 but this time with the variable (Berberine).\n\n\n TOMORROW IS DAY 1! ',
			reply_markup=reply_markup
		)

	if(query.data == "time_selected_0"):
		keyboard = [
			[
				InlineKeyboardButton("Understood", callback_data="consent_confirmed_1"),
			],
			
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		save_to_dict(user, "selectedTime", "9:00am")

		await update.effective_chat.send_message(
			f'You have chosen 9:00am.\n\n PLEASE REMEMBER TO FAST 3 HOURS PRIOR. \n\n ONLY WATER, NO FOOD! \n\n A reminder will be sent to you 3 hours prior to your selected time to STOP EATING! \n\n At the begining of your chosen time, please take your Baseline Glucose Reading (before eating).',
			reply_markup=reply_markup
		)

	if(query.data == "time_selected_1"):
		keyboard = [
			[
				InlineKeyboardButton("Understood", callback_data="consent_confirmed_1"),
			],
			
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		save_to_dict(user, "selectedTime", "12:00pm")

		await update.effective_chat.send_message(
			f'You have chosen 12:00pm.\n\n PLEASE REMEMBER TO FAST 3 HOURS PRIOR. \n\n ONLY WATER, NO FOOD! \n\n A reminder will be sent to you 3 hours prior to your selected time to STOP EATING! \n\n At the begining of your chosen time, please take your Baseline Glucose Reading (before eating).',
			reply_markup=reply_markup
		)

	if(query.data == "time_selected_2"):
		keyboard = [
			[
				InlineKeyboardButton("Understood", callback_data="consent_confirmed_1"),
			],
			
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		save_to_dict(user, "selectedTime", "3:00pm")

		await update.effective_chat.send_message(
			f'You have chosen 3:00pm.\n\n PLEASE REMEMBER TO FAST 3 HOURS PRIOR. \n\n ONLY WATER, NO FOOD! \n\n A reminder will be sent to you 3 hours prior to your selected time to STOP EATING! \n\n At the begining of your chosen time, please take your Baseline Glucose Reading (before eating).',
			reply_markup=reply_markup
		)

	if(query.data == "time_selected_3"):
		keyboard = [
			[
				InlineKeyboardButton("Understood", callback_data="consent_confirmed_1"),
			],
			
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		save_to_dict(user, "selectedTime", "6:00pm")

		await update.effective_chat.send_message(
			f'You have chosen 6:00pm.\n\n PLEASE REMEMBER TO FAST 3 HOURS PRIOR. \n\n ONLY WATER, NO FOOD! \n\n A reminder will be sent to you 3 hours prior to your selected time to STOP EATING! \n\n At the begining of your chosen time, please take your Baseline Glucose Reading (before eating).',
			reply_markup=reply_markup
		)



	if(query.data == "consent_confirmed_1"):
		keyboard = [
			[
				InlineKeyboardButton("200g Strawberries", callback_data="preferred_food_0"),
			],
			[
				InlineKeyboardButton("250ml Apple Juice", callback_data="preferred_food_1"),
			],
			[
				InlineKeyboardButton("Chocolate Bar", callback_data="preferred_food_2"),
			],
			[
				InlineKeyboardButton("Custom", callback_data="preferred_food_3"),
			],
			
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		await update.effective_chat.send_message(
			f'Once you have taken your Baseline Reading, it is now time for you to select your food.\n\n Pick something high in carbs and sugar, from the options below, or your own.\n\n Remember,this needs to be identical for day 1 and day 2.\n\n Once you eat the specified food, you must fast for 90 mins. \n\n\n After 90 minutes, take your Glucose Reading AGAIN!',
			reply_markup=reply_markup
		)

	if(query.data == "preferred_food_0"):
		keyboard = [
			[
				InlineKeyboardButton("Begin Trial", callback_data="consent_confirmed_2"),
			],
			
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		save_to_dict(user, "preferred_food", "Strawberries")

		await update.effective_chat.send_message(
			f'You are all set. Reminders will be sent to you in the chat to keep you on track! \n\n\n Thank you for participating and helping advance scientific discovery!',
			reply_markup=reply_markup
		)

	if(query.data == "preferred_food_1"):
		keyboard = [
			[
				InlineKeyboardButton("Begin Trial", callback_data="consent_confirmed_2"),
			],
			
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		save_to_dict(user, "preferred_food", "Apple Juice")

		await update.effective_chat.send_message(
			f'You are all set. Reminders will be sent to you in the chat to keep you on track! \n\n\n Thank you for participating and helping advance scientific discovery!',
			reply_markup=reply_markup
		)

	if(query.data == "preferred_food_2"):
		keyboard = [
			[
				InlineKeyboardButton("Begin Trial", callback_data="consent_confirmed_2"),
			],
			
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		save_to_dict(user, "preferred_food", "Chocolate Bar")

		await update.effective_chat.send_message(
			f'You are all set. Reminders will be sent to you in the chat to keep you on track! \n\n\n Thank you for participating and helping advance scientific discovery!',
			reply_markup=reply_markup
		)


	if(query.data == "preferred_food_3"):
		keyboard = [
			[
				InlineKeyboardButton("Begin Trial", callback_data="consent_confirmed_2"),
			],
		]

		reply_markup = InlineKeyboardMarkup(keyboard)	
		

		save_to_dict(user, "preferred_food", "Custom")

		await update.effective_chat.send_message(
			f'You are all set. Reminders will be sent to you in the chat to keep you on track! \n\n\n Thank you for participating and helping advance scientific discovery!',
			reply_markup=reply_markup
		)


	if(query.data == "consent_confirmed_2"):

		if not data_dict.get(str(user.id)):
			return

		if(data_dict[str(user.id)]["selectedTime"] == "9:00am"):
			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=9,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul"),
			) + datetime.timedelta(days=1) - datetime.timedelta(hours=3, minutes=15)
			
			job = sched.add_job(remind_fast, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=9,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2) - datetime.timedelta(hours=3, minutes=15)
			
			job = sched.add_job(remind_fast, "date", run_date=date, args=[[update, 1]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=9,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1)
			
			job = sched.add_job(remind_eat, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=9,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2)
			
			job = sched.add_job(remind_eat, "date", run_date=date, args=[[update, 1]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=9,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1) + datetime.timedelta(hours=3)
			
			job = sched.add_job(remind_update, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=9,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2) + datetime.timedelta(hours=3)
			
			job = sched.add_job(remind_update, "date", run_date=date, args=[[update, 1]])

			return

		if(data_dict[str(user.id)]["selectedTime"] == "12:00pm"):
			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=12,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1) - datetime.timedelta(hours=3, minutes=15)
			
			job = sched.add_job(remind_fast, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=12,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2) - datetime.timedelta(hours=3, minutes=15)
			
			job = sched.add_job(remind_fast, "date", run_date=date, args=[[update, 1]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=12,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1)
			
			job = sched.add_job(remind_eat, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=12,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2)
			
			job = sched.add_job(remind_eat, "date", run_date=date, args=[[update, 1]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=12,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1) + datetime.timedelta(hours=3)
			
			job = sched.add_job(remind_update, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=12,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2) + datetime.timedelta(hours=3)
			
			job = sched.add_job(remind_update, "date", run_date=date, args=[[update, 1]])

			return
		if(data_dict[str(user.id)]["selectedTime"] == "3:00pm"):
			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=15,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1) - datetime.timedelta(hours=3, minutes=15)
			
			job = sched.add_job(remind_fast, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=15,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2) - datetime.timedelta(hours=3, minutes=15)
			
			job = sched.add_job(remind_fast, "date", run_date=date, args=[[update, 1]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=15,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1)
			
			job = sched.add_job(remind_eat, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=15,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2)
			
			job = sched.add_job(remind_eat, "date", run_date=date, args=[[update, 1]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=15,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1) + datetime.timedelta(hours=3)
			
			job = sched.add_job(remind_update, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=15,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2) + datetime.timedelta(hours=3)
			
			job = sched.add_job(remind_update, "date", run_date=date, args=[[update, 1]])

			return
		if(data_dict[str(user.id)]["selectedTime"] == "6:00pm"):
			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=18,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1) - datetime.timedelta(hours=3, minutes=15)
			
			job = sched.add_job(remind_fast, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=18,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2) - datetime.timedelta(hours=3, minutes=15)
			
			job = sched.add_job(remind_fast, "date", run_date=date, args=[[update, 1]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=18,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1)
			
			job = sched.add_job(remind_eat, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=18,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2)
			
			job = sched.add_job(remind_eat, "date", run_date=date, args=[[update, 1]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=18,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=1) + datetime.timedelta(hours=3)
			
			job = sched.add_job(remind_update, "date", run_date=date, args=[[update, 0]])

			date = datetime.datetime(
				datetime.date.today().year,
				datetime.date.today().month,
				datetime.date.today().day,
				hour=18,
				minute=0,
				second=0,
				tzinfo=pytz.timezone("Europe/Istanbul")
			) + datetime.timedelta(days=2) + datetime.timedelta(hours=3)
			
			job = sched.add_job(remind_update, "date", run_date=date, args=[[update, 1]])

			return


		await update.effective_chat.send_message(
			f'You are all set. The trial has begun. A reminder will be sent to you at your selected time.',
		)		


app = ApplicationBuilder().token("6807246684:AAH-3hWq99wQpkLs_N0yvUcHJZ2cE3aIJ0U").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))

app.run_polling()