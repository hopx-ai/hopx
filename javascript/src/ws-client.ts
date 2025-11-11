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
   * Receive JSON message
   */
  async receive(ws: WebSocket): Promise<any> {
    return new Promise((resolve, reject) => {
      ws.once('message', (data) => {
        try {
          resolve(JSON.parse(data.toString()));
        } catch (error) {
          reject(error);
        }
      });
      ws.once('error', reject);
    });
  }

  /**
   * Async iterator for messages
   */
  async *messages(ws: WebSocket): AsyncIterableIterator<any> {
    while (ws.readyState === WebSocket.OPEN) {
      try {
        const message = await this.receive(ws);
        yield message;
      } catch (error) {
        break;
      }
    }
  }
}

