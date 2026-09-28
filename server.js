const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3000;
const ROOT = __dirname;

const MIME = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

function send(res, status, body, type = 'text/plain') {
  res.writeHead(status, { 'Content-Type': type });
  res.end(body);
}

function serveStatic(req, res) {
  let urlPath = decodeURIComponent(req.url.split('?')[0]);
  if (urlPath === '/') urlPath = '/index.html';
  const filePath = path.join(ROOT, path.normalize(urlPath).replace(/^(\.\.[\/\\])+/, ''));

  if (!filePath.startsWith(ROOT)) return send(res, 403, 'Forbidden');

  fs.readFile(filePath, (err, data) => {
    if (err) {
      if (err.code === 'ENOENT') {
        // SPA fallback: serve index.html for unknown routes (except /api)
        if (!req.url.startsWith('/api')) {
          fs.readFile(path.join(ROOT, 'index.html'), (e2, d2) => {
            if (e2) return send(res, 404, 'Not found');
            send(res, 200, d2, 'text/html');
          });
        } else {
          send(res, 404, JSON.stringify({ error: 'Not found' }), 'application/json');
        }
      } else {
        send(res, 500, 'Server error');
      }
      return;
    }
    send(res, 200, data, MIME[path.extname(filePath).toLowerCase()] || 'application/octet-stream');
  });
}

const server = http.createServer((req, res) => {
  console.log(`${req.method} ${req.url}`);

  // Simple demo API
  if (req.url === '/api/hello' && req.method === 'GET') {
    return send(res, 200, JSON.stringify({ message: 'Hello! Thanks for visiting.' }), 'application/json');
  }

  if (req.url === '/api/contact' && req.method === 'POST') {
    let body = '';
    req.on('data', (chunk) => (body += chunk));
    req.on('end', () => {
      try {
        const { name = 'friend', email = '' } = JSON.parse(body || '{}');
        send(
          res,
          200,
          JSON.stringify({ message: `Thanks, ${name}! I'll get back to you soon.`, email }),
          'application/json'
        );
      } catch {
        send(res, 400, JSON.stringify({ error: 'Invalid JSON' }), 'application/json');
      }
    });
    return;
  }

  if (req.method !== 'GET') return send(res, 405, 'Method not allowed');
  serveStatic(req, res);
});

server.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
