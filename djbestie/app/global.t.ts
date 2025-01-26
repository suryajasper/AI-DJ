// global.d.ts
export {};

declare global {
  interface Window {
    sendMessageToUnity: (gameObjectName: string, methodName: string, parameter?: any) => void;
  }
}
