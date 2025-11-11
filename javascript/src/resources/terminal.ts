/**
 * Terminal resource - Interactive terminal via WebSocket
 */

import WebSocket from 'ws';
import { WSClient } from '../ws-client.js';
import type { TerminalMessage } from '../types/index.js';

export class Terminal {
  constructor(private wsClient: WSClient) {}

  /**
   * Connect to interactive terminal
   */
  async connect(): Promise<WebSocket> {
    return this.wsClient.connect('/terminal');
  }

  /**
   * Send input to terminal
   */
  sendInput(ws: WebSocket, data: string): void {
    this.wsClient.send(ws, { type: 'input', data });
  }

  /**
   * Resize terminal
   */
  resize(ws: WebSocket, cols: number, rows: number): void {
    this.wsClient.send(ws, { type: 'resize', cols, rows });
  }

  /**
   * Async iterator for terminal output
   */
  async *output(ws: WebSocket): AsyncIterableIterator<TerminalMessage> {
    for await (const message of this.wsClient.messages(ws)) {
      yield message as TerminalMessage;
      if (message.type === 'exit') {
        break;
      }
    }
  }
}

