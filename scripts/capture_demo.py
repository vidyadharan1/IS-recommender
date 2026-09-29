import subprocess
import time
import json
import urllib.request
import base64
import asyncio
import websockets

async def send_cmd(ws, msg_id, method, params=None):
    payload = {"id": msg_id, "method": method}
    if params:
        payload["params"] = params
    await ws.send(json.dumps(payload))
    while True:
        raw = await ws.recv()
        data = json.loads(raw)
        if data.get("id") == msg_id:
            return data

async def capture_fe500d_screenshot():
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    proc = subprocess.Popen([
        edge_path,
        "--headless=new",
        "--remote-debugging-port=9222",
        "--disable-gpu",
        "--window-size=1440,1200",
        "http://localhost:5173"
    ])
    
    time.sleep(2.5)
    
    try:
        req = urllib.request.urlopen("http://localhost:9222/json")
        targets = json.loads(req.read().decode())
        page_target = next(t for t in targets if t.get("type") == "page")
        ws_url = page_target["webSocketDebuggerUrl"]
        
        async with websockets.connect(ws_url) as ws:
            await send_cmd(ws, 1, "Page.enable")
            await send_cmd(ws, 2, "Runtime.enable")
            
            await asyncio.sleep(2.0)
            
            action_script = """
            (async () => {
                const allButtons = Array.from(document.querySelectorAll('button'));
                const feBtn = allButtons.find(b => b.innerText.includes('Fe 500D'));
                if (feBtn) feBtn.click();
                
                await new Promise(r => setTimeout(r, 800));
                
                const submitBtn = document.querySelector('.submit-btn');
                if (submitBtn) submitBtn.click();
                
                for (let i = 0; i < 30; i++) {
                    await new Promise(r => setTimeout(r, 400));
                    const resContainer = document.querySelector('.results-container, .rec-card');
                    if (resContainer) {
                        resContainer.scrollIntoView({ behavior: 'instant', block: 'start' });
                        break;
                    }
                }
            })()
            """
            
            await send_cmd(ws, 3, "Runtime.evaluate", {
                "expression": action_script,
                "awaitPromise": True
            })
            
            await asyncio.sleep(1.0)
            
            resp = await send_cmd(ws, 4, "Page.captureScreenshot", {"format": "png"})
            img_data = base64.b64decode(resp["result"]["data"])
            
            artifact_dir = r"C:\Users\ashwin\.gemini\antigravity-ide\brain\17fba9c9-bcb8-40be-ab24-0326257eedf3"
            artifact_path = f"{artifact_dir}\\fe500d_recommendations_verified.png"
            with open(artifact_path, "wb") as f:
                f.write(img_data)
                
            local_path = "fe500d_recommendations_verified.png"
            with open(local_path, "wb") as f:
                f.write(img_data)
                
            print(f"[SUCCESS] Scrolled results screenshot saved to {artifact_path}")
            
    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(capture_fe500d_screenshot())
