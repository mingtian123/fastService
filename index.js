/**
 * fastService - 快速服务框架入口
 */

const http = require('http');

const PORT = process.env.PORT || 3000;

const server = http.createServer((req, res) => {
  res.writeHead(200, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({
    service: 'fastService',
    version: '1.0.0',
    status: 'running',
    timestamp: new Date().toISOString()
  }));
});

server.listen(PORT, () => {
  console.log(`fastService is running on port ${PORT}`);
});

module.exports = server;
