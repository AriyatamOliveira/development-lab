const chalk = {
  cyan: (text) => `\x1b[36m${text}\x1b[0m`,
  green: (text) => `\x1b[32m${text}\x1b[0m`,
  yellow: (text) => `\x1b[33m${text}\x1b[0m`,
  red: (text) => `\x1b[31m${text}\x1b[0m`,
  magenta: (text) => `\x1b[35m${text}\x1b[0m`,
  dim: (text) => `\x1b[2m${text}\x1b[0m`,
  bold: (text) => `\x1b[1m${text}\x1b[0m`,
  reset: () => `\x1b[0m`
};

const timestamp = () => {
  const now = new Date();
  return now.toISOString().split('T')[1].slice(0, 8);
};

const logger = {
  info: (msg) => console.log(`[${timestamp()}] ${chalk.cyan('[INFO]')} ${msg}`),
  success: (msg) => console.log(`[${timestamp()}] ${chalk.green('[SUCCESS]')} ${msg}`),
  warn: (msg) => console.log(`[${timestamp()}] ${chalk.yellow('[WARN]')} ${msg}`),
  error: (msg) => console.log(`[${timestamp()}] ${chalk.red('[ERROR]')} ${msg}`),
  scan: (type, msg) => console.log(`[${timestamp()}] ${chalk.magenta(`[${type.toUpperCase()} SCAN]`)} ${msg}`),
  divider: () => console.log(chalk.dim('─'.repeat(60)))
};

module.exports = logger;
