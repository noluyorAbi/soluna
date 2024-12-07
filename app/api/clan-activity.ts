// pages/api/clan-activity.js

import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';

export default function handler(req, res) {
  const scriptPath = path.resolve('path/to/your/script.py');

  exec(`python ${scriptPath}`, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
      return res.status(500).json({ error: 'Internal Server Error' });
    }
    // Read the generated HTML file
    fs.readFile('clan_activity_plot.html', 'utf8', (err, data) => {
      if (err) {
        console.error('Error reading HTML file:', err);
        return res.status(500).json({ error: 'Internal Server Error' });
      }
      res.setHeader('Content-Type', 'text/html');
      res.send(data);
    });
  });
}
