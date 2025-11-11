/**
 * Desktop resource - Desktop automation and VNC
 */

import { HTTPClient } from '../client.js';
import type {
  VNCInfo,
  WindowInfo,
  RecordingInfo,
  DisplayInfo,
  ScreenshotResponse,
  MouseClickOptions,
  OCROptions,
} from '../types/index.js';

export class Desktop {
  constructor(private client: HTTPClient) {}

  // ==========================================================================
  // VNC
  // ==========================================================================

  async startVnc(): Promise<VNCInfo> {
    return this.client.get<VNCInfo>('/desktop/vnc/start');
  }

  async stopVnc(): Promise<void> {
    await this.client.get('/desktop/vnc/stop');
  }

  async getVncInfo(): Promise<VNCInfo> {
    return this.client.get<VNCInfo>('/desktop/vnc/info');
  }

  async getVncUrl(): Promise<string> {
    const info = await this.getVncInfo();
    return info.url || '';
  }

  // ==========================================================================
  // MOUSE
  // ==========================================================================

  async mouseClick(x: number, y: number, options?: MouseClickOptions): Promise<void> {
    await this.client.post('/desktop/mouse/click', {
      x,
      y,
      button: options?.button ?? 'left',
      clicks: options?.clicks ?? 1,
    });
  }

  async mouseMove(x: number, y: number): Promise<void> {
    await this.client.post('/desktop/mouse/move', { x, y });
  }

  async mouseDrag(fromX: number, fromY: number, toX: number, toY: number): Promise<void> {
    await this.client.post('/desktop/mouse/drag', {
      from_x: fromX,
      from_y: fromY,
      to_x: toX,
      to_y: toY,
    });
  }

  async mouseScroll(x: number, y: number, deltaY: number): Promise<void> {
    await this.client.post('/desktop/mouse/scroll', { x, y, delta_y: deltaY });
  }

  // ==========================================================================
  // KEYBOARD
  // ==========================================================================

  async keyboardType(text: string): Promise<void> {
    await this.client.post('/desktop/keyboard/type', { text });
  }

  async keyboardPress(key: string): Promise<void> {
    await this.client.post('/desktop/keyboard/press', { key });
  }

  async keyboardCombination(keys: string[]): Promise<void> {
    await this.client.post('/desktop/keyboard/combination', { keys });
  }

  // ==========================================================================
  // CLIPBOARD
  // ==========================================================================

  async getClipboard(): Promise<string> {
    const response = await this.client.get<{ content: string }>('/desktop/clipboard/get');
    return response.content;
  }

  async setClipboard(content: string): Promise<void> {
    await this.client.post('/desktop/clipboard/set', { content });
  }

  async getClipboardHistory(): Promise<string[]> {
    const response = await this.client.get<{ history: string[] }>('/desktop/clipboard/history');
    return response.history;
  }

  // ==========================================================================
  // SCREENSHOT & RECORDING
  // ==========================================================================

  async screenshot(): Promise<ScreenshotResponse> {
    return this.client.get<ScreenshotResponse>('/desktop/screenshot');
  }

  async screenshotRegion(x: number, y: number, width: number, height: number): Promise<Buffer> {
    const response = await this.client.post<ArrayBuffer>('/desktop/screenshot/region', { x, y, width, height });
    return Buffer.from(response);
  }

  async startRecording(outputFile?: string): Promise<void> {
    await this.client.post('/desktop/recording/start', { output_file: outputFile });
  }

  async stopRecording(): Promise<void> {
    await this.client.post('/desktop/recording/stop');
  }

  async getRecordingStatus(): Promise<RecordingInfo> {
    return this.client.get<RecordingInfo>('/desktop/recording/status');
  }

  async downloadRecording(recordingId: string): Promise<Buffer> {
    const response = await this.client.get<ArrayBuffer>(`/desktop/recording/${recordingId}/download`);
    return Buffer.from(response);
  }

  // ==========================================================================
  // WINDOWS
  // ==========================================================================

  async listWindows(): Promise<WindowInfo[]> {
    const response = await this.client.get<{ windows: WindowInfo[] }>('/desktop/windows/list');
    return response.windows;
  }

  async focusWindow(windowId: string): Promise<void> {
    await this.client.post('/desktop/windows/focus', { window_id: windowId });
  }

  async closeWindow(windowId: string): Promise<void> {
    await this.client.post('/desktop/windows/close', { window_id: windowId });
  }

  async minimizeWindow(windowId: string): Promise<void> {
    await this.client.post('/desktop/windows/minimize', { window_id: windowId });
  }

  async resizeWindow(windowId: string, width: number, height: number): Promise<void> {
    await this.client.post('/desktop/windows/resize', { window_id: windowId, width, height });
  }

  // ==========================================================================
  // DISPLAY
  // ==========================================================================

  async getDisplayInfo(): Promise<DisplayInfo> {
    return this.client.get<DisplayInfo>('/desktop/display/info');
  }

  async setResolution(width: number, height: number): Promise<void> {
    await this.client.post('/desktop/display/resolution', { width, height });
  }

  async getAvailableResolutions(): Promise<[number, number][]> {
    const response = await this.client.get<{ resolutions: [number, number][] }>('/desktop/display/resolutions');
    return response.resolutions;
  }

  // ==========================================================================
  // X11 ADVANCED
  // ==========================================================================

  async ocr(x: number, y: number, width: number, height: number, options?: OCROptions): Promise<string> {
    const response = await this.client.post<{ text: string }>('/desktop/x11/ocr', {
      x,
      y,
      width,
      height,
      language: options?.language ?? 'eng',
    });
    return response.text;
  }

  async findElement(text: string): Promise<{ x: number; y: number; width: number; height: number } | null> {
    const response = await this.client.post<{ element?: any }>('/desktop/x11/find_element', { text });
    return response.element ?? null;
  }

  async waitFor(text: string, timeout = 30): Promise<{ x: number; y: number; width: number; height: number }> {
    const response = await this.client.post<{ element: any }>('/desktop/x11/wait_for', {
      text,
      timeout,
    });
    return response.element;
  }

  async dragDrop(fromX: number, fromY: number, toX: number, toY: number): Promise<void> {
    await this.client.post('/desktop/x11/drag_drop', {
      from_x: fromX,
      from_y: fromY,
      to_x: toX,
      to_y: toY,
    });
  }

  async getBounds(text: string): Promise<{ x: number; y: number; width: number; height: number }> {
    return this.client.post<{ x: number; y: number; width: number; height: number }>(
      '/desktop/x11/get_bounds',
      { text }
    );
  }

  async captureWindow(windowId?: string): Promise<Buffer> {
    const response = await this.client.get<ArrayBuffer>('/desktop/x11/capture_window', {
      params: windowId ? { window_id: windowId } : undefined,
      responseType: 'arraybuffer',
    });
    return Buffer.from(response);
  }
}

