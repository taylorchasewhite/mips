// Pinned runtime; Python and user programs execute only inside this worker.
const runtimeURL = "https://cdn.jsdelivr.net/pyodide/v314.0.8/full/pyodide.mjs";
let compile;

async function initialize() {
    const {loadPyodide} = await import(runtimeURL);
    const runtime = await loadPyodide();
    runtime.FS.mkdir("/mips");
    await Promise.all(["compiler.py", "lexer.py", "codeGen.py", "record.py"].map(async (name) => {
        const response = await fetch(new URL("../part6/" + name, import.meta.url));
        if (!response.ok) throw new Error("Cannot load " + name + " (HTTP " + response.status + ").");
        runtime.FS.writeFile("/mips/" + name, await response.text());
    }));
    runtime.runPython(`
import sys
import json
sys.path.insert(0, "/mips")
from compiler import compile_source

def compile_json(source):
    try:
        return json.dumps({"assembly": compile_source(source)})
    except ValueError as error:
        return json.dumps({"error": str(error)})
`);
    compile = runtime.globals.get("compile_json");
    self.postMessage({type: "ready"});
}

self.onmessage = (event) => {
    if (event.data.type !== "compile") return;
    try {
        const result = JSON.parse(compile(event.data.source));
        self.postMessage({type: "result", ...result});
    } catch (error) {
        console.error(error);
        self.postMessage({type: "fatal", error: "Compiler failed unexpectedly: " + error.message});
    }
};

initialize().catch((error) => {
    console.error(error);
    self.postMessage({type: "fatal", error: "Unable to load the compiler: " + error.message});
});
