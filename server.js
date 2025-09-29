import express from 'express';
import cors from 'cors';
import fs from 'fs';
import path from 'path';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('dist'));

// File paths
const CONFIG_FILE = 'bot_config.json';
const LOG_FILE = 'tweet_log.json';
const POSTED_LINKS_FILE = 'posted_links.txt';

// Helper function to read JSON files safely
const readJSONFile = (filePath, defaultValue = {}) => {
  try {
    if (fs.existsSync(filePath)) {
      const data = fs.readFileSync(filePath, 'utf8');
      return JSON.parse(data);
    }
    return defaultValue;
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error);
    return defaultValue;
  }
};

// Helper function to write JSON files safely
const writeJSONFile = (filePath, data) => {
  try {
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2));
    return true;
  } catch (error) {
    console.error(`Error writing ${filePath}:`, error);
    return false;
  }
};

// API Routes

// Get bot configuration
app.get('/api/config', (req, res) => {
  const config = readJSONFile(CONFIG_FILE, {});
  res.json(config);
});

// Update bot configuration
app.put('/api/config', (req, res) => {
  const success = writeJSONFile(CONFIG_FILE, req.body);
  if (success) {
    res.json({ message: 'Configuration updated successfully' });
  } else {
    res.status(500).json({ error: 'Failed to update configuration' });
  }
});

// Get tweet logs
app.get('/api/logs', (req, res) => {
  const logs = readJSONFile(LOG_FILE, []);
  // Sort by timestamp descending (newest first)
  const sortedLogs = logs.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  res.json(sortedLogs);
});

// Get bot statistics
app.get('/api/stats', (req, res) => {
  const logs = readJSONFile(LOG_FILE, []);
  const today = new Date().toISOString().split('T')[0];
  
  const todayLogs = logs.filter(log => log.timestamp.startsWith(today));
  const successfulTweets = logs.filter(log => log.success).length;
  const failedTweets = logs.filter(log => !log.success).length;
  
  // Read posted links to get total count
  let totalPostedLinks = 0;
  try {
    if (fs.existsSync(POSTED_LINKS_FILE)) {
      const content = fs.readFileSync(POSTED_LINKS_FILE, 'utf8');
      totalPostedLinks = content.split('\n').filter(line => line.trim()).length;
    }
  } catch (error) {
    console.error('Error reading posted links:', error);
  }

  res.json({
    totalTweets: logs.length,
    todayTweets: todayLogs.length,
    successfulTweets,
    failedTweets,
    totalPostedLinks,
    successRate: logs.length > 0 ? ((successfulTweets / logs.length) * 100).toFixed(1) : 0
  });
});

// Run bot manually
app.post('/api/run-bot', (req, res) => {
  try {
    const pythonProcess = spawn('python', ['main.py'], {
      stdio: 'pipe',
      cwd: process.cwd()
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      output += data.toString();
      console.log('Bot output:', data.toString());
    });

    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString();
      console.error('Bot error:', data.toString());
    });

    pythonProcess.on('close', (code) => {
      if (code === 0) {
        res.json({ 
          success: true, 
          message: 'Bot executed successfully',
          output: output
        });
      } else {
        res.status(500).json({ 
          success: false, 
          message: 'Bot execution failed',
          error: errorOutput,
          output: output
        });
      }
    });

    // Set timeout for long-running processes
    setTimeout(() => {
      pythonProcess.kill();
      res.status(408).json({ 
        success: false, 
        message: 'Bot execution timed out',
        output: output
      });
    }, 300000); // 5 minutes timeout

  } catch (error) {
    res.status(500).json({ 
      success: false, 
      message: 'Failed to start bot',
      error: error.message 
    });
  }
});

// Clear logs
app.delete('/api/logs', (req, res) => {
  try {
    fs.writeFileSync(LOG_FILE, '[]');
    res.json({ message: 'Logs cleared successfully' });
  } catch (error) {
    res.status(500).json({ error: 'Failed to clear logs' });
  }
});

// Serve React app for all other routes
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
});