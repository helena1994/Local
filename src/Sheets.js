const { GoogleSpreadsheet } = require('google-spreadsheet');
require('dotenv').config();

const doc = new GoogleSpreadsheet(process.env.GOOGLE_SHEET_ID);

const auth = async () => {
  await doc.useServiceAccountAuth(require('../credentials/service-account.json'));
  await doc.loadInfo();
};

module.exports = {
  readSheet: async () => {
    await auth();
    const sheet = doc.sheetsByIndex[0];
    const rows = await sheet.getRows();
    return rows.map(row => row.get('Data'));
  },

  writeSheet: async (data) => {
    await auth();
    const sheet = doc.sheetsByIndex[0];
    await sheet.addRow({ 
      Data: data, 
      Tanggal: new Date().toLocaleString('id-ID') 
    });
  }
};
