class Logger {
  constructor() {
    this.levels = {
      error: 0,
      warn: 1,
      info: 2,
      debug: 3
    };

    this.currentLevel = this.levels[process.env.LOG_LEVEL || 'info'] || 2;
  }

  /**
   * Get current timestamp
   */
  timestamp() {
    const now = new Date();
    return now.toISOString().split('T')[1].slice(0, 8);
  }

  /**
   * Log error message
   */
  error(msg) {
    if (this.currentLevel >= this.levels.error) {
      console.log(`[${this.timestamp()}] [\x1b[31mERROR\x1b[0m] ${msg}`);
    }
  }

  /**
   * Log warning message
   */
  warn(msg) {
    if (this.currentLevel >= this.levels.warn) {
      console.log(`[${this.timestamp()}] [\x1b[33mWARN\x1b[0m] ${msg}`);
    }
  }

  /**
   * Log info message
   */
  info(msg) {
    if (this.currentLevel >= this.levels.info) {
      console.log(`[${this.timestamp()}] [\x1b[36mINFO\x1b[0m] ${msg}`);
    }
  }

  /**
   * Log debug message
   */
  debug(msg) {
    if (this.currentLevel >= this.levels.debug) {
      console.log(`[${this.timestamp()}] [\x1b[35mDEBUG\x1b[0m] ${msg}`);
    }
  }

  /**
   * Log success message
   */
  success(msg) {
    if (this.currentLevel >= this.levels.info) {
      console.log(`[${this.timestamp()}] [\x1b[32mSUCCESS\x1b[0m] ${msg}`);
    }
  }

  /**
   * Log scan message
   */
  scan(type, msg) {
    if (this.currentLevel >= this.levels.info) {
      console.log(`[${this.timestamp()}] [\x1b[35m${type.toUpperCase()} SCAN\x1b[0m] ${msg}`);
    }
  }

  /**
   * Log divider
   */
  divider() {
    console.log('\x1b[2m' + '─'.repeat(60) + '\x1b[0m');
  }
}

module.exports = Logger;