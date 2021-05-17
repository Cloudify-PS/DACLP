const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const port = process.env.PORT || 80;
const https_port = process.env.HTTPS_PORT || 443;
const index = fs.readFileSync(path.join(process.cwd(), 'app', 'index.html'));

// HTTP server
const server = http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end(index);
})

server.listen(port, () => {
  console.log(`Server running on http://localhost:${port}/`);
});

// HTTPS server
const options = {
  key: fs.readFileSync(path.join(process.cwd(), 'app', 'server.rsa')),
  cert: fs.readFileSync(path.join(process.cwd(), 'app', 'server.crt'))
};

const https_server = https.createServer(options, function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/html'});
  res.end(index);
})

https_server.listen(https_port, () => {
  console.log(`Server running on https://localhost:${https_port}/`);
});
