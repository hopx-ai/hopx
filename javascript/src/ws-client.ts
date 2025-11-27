/**
 * WebSocket client for real-time streaming
 */

import WebSocket from 'ws';

export class WSClient {
  private wsBaseUrl: string;
  private jwtToken?: string;

  constructor(agentUrl: string, jwtToken?: string) {
    // Convert https:// to wss://
    const url = new URL(agentUrl);
    const wsScheme = url.protocol === 'https:' ? 'wss:' : 'ws:';
    this.wsBaseUrl = `${wsScheme}//${url.host}`;
    this.jwtToken = jwtToken;
  }

  /**
   * Connect to WebSocket endpoint with JWT authentication
   */
  async connect(endpoint: string): Promise<WebSocket> {
    const url = `${this.wsBaseUrl}${endpoint}`;
    
    // Create WebSocket with JWT token in Authorization header
    const wsOptions: any = {};
    if (this.jwtToken) {
      wsOptions.headers = {
        'Authorization': `Bearer ${this.jwtToken}`
      };
    }
    
    const ws = new WebSocket(url, wsOptions);

    return new Promise((resolve, reject) => {
      ws.on('open', () => resolve(ws));
      ws.on('error', reject);
    });
  }
  
  /**
   * Update JWT token for future WebSocket connections
   */
  updateJwtToken(token: string): void {
    this.jwtToken = token;
  }

  /**
   * Send JSON message
   */
  send(ws: WebSocket, message: any): void {
    ws.send(JSON.stringify(message));
  }

  /**
   * Receive JSON message with empty message protection
   */
  async receive(ws: WebSocket): Promise<any> {
    return new Promise((resolve, reject) => {
      const onMessage = (data: WebSocket.Data) => {
        try {
          // Convert to string
          const message = typeof data === 'string' ? data : data.toString('utf-8');

          // Skip empty messages
          if (!message || !message.trim()) {
            // Re-attach listener for next message
            ws.once('message', onMessage);
            return;
          }

          // Parse JSON
          try {
            resolve(JSON.parse(message));
          } catch (parseError) {
            // Log invalid JSON and wait for next message
            console.warn(`Skipping invalid JSON: ${message.slice(0, 100)}`);
            ws.once('message', onMessage);
          }
        } catch (error) {
          reject(error);
        }
      };

      ws.once('message', onMessage);
      ws.once('error', reject);
    });
  }

  /**
   * Async iterator for messages with empty message protection
   */
  async *messages(ws: WebSocket): AsyncIterableIterator<any> {
    while (ws.readyState === WebSocket.OPEN) {
      try {
        const message = await this.receive(ws);
        if (message !== undefined) {
          yield message;
        }
      } catch (error) {
        break;
      }
    }
  }
}

