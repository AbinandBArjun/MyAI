
import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const ollamaUrl = "http://localhost:11434/api/tags";

async function ollamaIsReady() {
    try {
        const response = await fetch(ollamaUrl, {
            signal: AbortSignal.timeout(2000),
        });
        return response.ok;
    } catch {
        return false;
    }
}

async function ensureOllama() {
    if (await ollamaIsReady()) {
        console.log("[OLLAMA] Already running.");
        return;
    }

    console.log("[OLLAMA] Starting local model server...");

    const ollama = spawn("ollama", ["serve"], {
        stdio: "inherit",
        windowsHide: true,
    });

    ollama.on("error", (error) => {
        console.error("[OLLAMA] Could not start Ollama:", error.message);
    });

    for (let attempt = 0; attempt < 30; attempt++) {
        await delay(1000);

        if (await ollamaIsReady()) {
            console.log("[OLLAMA] Ready.");
            return;
        }

        if (ollama.exitCode !== null) {
            throw new Error("Ollama exited before its API became ready.");
        }
    }

    throw new Error(
        "Ollama did not become ready within 30 seconds. Check the Ollama installation."
    );
}

await ensureOllama();

const processes = spawn(
    "npx",
    [
        "concurrently",
        "--kill-others-on-fail",
        "--names",
        "BACKEND,FRONTEND",
        "--prefix-colors",
        "blue,green",
        "npm:dev:backend",
        "npm:dev:frontend",
    ],
    {
        stdio: "inherit",
        shell: true,
    }
);

const shutdown = () => {
    if (processes.exitCode === null) {
        processes.kill();
    }
};

process.on("SIGINT", shutdown);
process.on("SIGTERM", shutdown);

processes.on("exit", (code) => {
    process.exitCode = code ?? 1;
});
