require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const { readSheet, writeSheet } = require('./sheets');

const bot = new TelegramBot(process.env.TELEGRAM_TOKEN, { polling: true });

bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, '🤖 Bot siap! Gunakan:\n/read - Baca data\n/write [text] - Simpan data');
});

bot.onText(/\/read/, async (msg) => {
  try {
    const data = await readSheet();
    bot.sendMessage(msg.chat.id, `📊 Data terbaru:\n${data.join('\n')}`);
  } catch (error) {
    bot.sendMessage(msg.chat.id, '❌ Gagal membaca data');
  }
});

bot.onText(/\/write (.+)/, async (msg, match) => {
  try {
    await writeSheet(match[1]);
    bot.sendMessage(msg.chat.id, `✅ Data "${match[1]}" tersimpan!`);
  } catch (error) {
    bot.sendMessage(msg.chat.id, '❌ Gagal menyimpan data');
  }
});

console.log('Bot berjalan...');
