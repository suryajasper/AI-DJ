import React, { useRef, useEffect } from "react";
import { Unity, useUnityContext } from "react-unity-webgl";

function DJ() {
  const { unityProvider } = useUnityContext({
    loaderUrl: "build/Build/build.loader.js",
    dataUrl: "build/Build/build.data",
    frameworkUrl: "build/Build/build.framework.js",
    codeUrl: "build/Build/build.wasm",
  });

  const unityRef = useRef<any>(null);
  
  const sendMessageToUnity = (gameObjectName: string, methodName: string, parameter?: any) => {
    if (unityRef.current) {
      unityRef.current.SendMessage(gameObjectName, methodName, parameter);
    }
  };
  
  useEffect(() => {
    window.sendMessageToUnity = sendMessageToUnity;
  }, []);

  return <Unity ref={unityRef} unityProvider={unityProvider} style={{ width: "100%", height: "100%" }} />;
}

export default DJ;
