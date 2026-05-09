from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

from database import users
from config import BOT_TOKEN, BOT_USERNAME
from game import deal_cards, compare

START_CHIPS = 5000
REFERRAL_BONUS = 1000


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user
    user_id = user.id

    existing = users.find_one({"user_id": user_id})

    referrer_id = None

    if context.args:
        try:
            referrer_id = int(context.args[0])
        except:
            pass

    if not existing:

        users.insert_one({
            "user_id": user_id,
            "name": user.first_name,
            "chips": START_CHIPS,
            "referrals": 0
        })

        if referrer_id and referrer_id != user_id:

            users.update_one(
                {"user_id": referrer_id},
                {
                    "$inc": {
                        "chips": REFERRAL_BONUS,
                        "referrals": 1
                    }
                }
            )

    keyboard = [
        [InlineKeyboardButton("🎮 Play", callback_data="play")],
        [InlineKeyboardButton("👤 Profile", callback_data="profile")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎴 Welcome to Teen Patti BD Bot!",
        reply_markup=reply_markup
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    user = users.find_one({"user_id": user_id})

    if query.data == "profile":

        referral_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"

        text = (
            f"👤 Name: {user['name']}\n"
            f"💰 Chips: {user['chips']}\n"
            f"👥 Referrals: {user['referrals']}\n\n"
            f"🔗 Referral Link:\n{referral_link}"
        )

        await query.message.reply_text(text)

    elif query.data == "leaderboard":

        top_users = users.find().sort("chips", -1).limit(10)

        text = "🏆 Leaderboard\n\n"

        rank = 1

        for u in top_users:
            text += f"{rank}. {u['name']} - {u['chips']} chips\n"
            rank += 1

        await query.message.reply_text(text)

    elif query.data == "play":

        player_cards = deal_cards()
        bot_cards = deal_cards()

        winner = compare(player_cards, bot_cards)

        reward = 500

        if winner == "player":

            users.update_one(
                {"user_id": user_id},
                {"$inc": {"chips": reward}}
            )

            result = f"🎉 You Won +{reward} chips!"

        elif winner == "bot":

            users.update_one(
                {"user_id": user_id},
                {"$inc": {"chips": -reward}}
            )

            result = f"😢 You Lost -{reward} chips!"

        else:

            result = "🤝 Draw Match!"

        text = (
            f"🃏 Your Cards:\n{' '.join(player_cards)}\n\n"
            f"🤖 Bot Cards:\n{' '.join(bot_cards)}\n\n"
            f"{result}"
        )

        play_again_keyboard = [
            [InlineKeyboardButton("🔄 Play Again", callback_data="play")]
        ]

        reply_markup = InlineKeyboardMarkup(play_again_keyboard)

        await query.message.reply_text(
            text,
            reply_markup=reply_markup
        )


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))

print("Teen Patti Bot Running...")

app.run_polling()