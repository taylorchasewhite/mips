"use strict";

function initializeCompiler() {
    document.querySelectorAll(".tabs").forEach(function (element) {
        new CBPFWTabs(element);
    });
    var source = ace.edit("editor0");
    var output = ace.edit("editor1");
    [source, output].forEach(function (editor) {
        editor.setOptions({fontSize: "14px", showPrintMargin: false});
        editor.getSession().setMode("ace/mode/text");
        editor.getSession().setUseWrapMode(true);
        editor.$blockScrolling = Infinity;
    });
    source.textInput.getElement().setAttribute("aria-label", "Source program");
    output.textInput.getElement().setAttribute("aria-label", "MIPS assembly output");
    output.setReadOnly(true);

    var compile = document.getElementById("btnCompile");
    var download = document.getElementById("btnDownload");
    var status = document.getElementById("parseErrorDiv");
    var worker;
    var ready = false;
    var pending = false;
    var revision = 0;
    var compilingRevision = 0;
    var timer;

    function report(message, error) {
        status.textContent = message;
        status.className = error ? "parseError" : "";
    }

    function failed(message) {
        clearTimeout(timer);
        if (worker) worker.terminate();
        ready = false;
        pending = false;
        output.setValue("", -1);
        download.disabled = true;
        compile.disabled = false;
        compile.textContent = "Retry compiler";
        report(message, true);
    }

    function start() {
        compile.disabled = true;
        report("Loading Python runtime (first visit requires a download)...");
        timer = setTimeout(function () {
            failed("Compiler loading timed out. Check your connection and retry.");
        }, 120000);
        try {
            worker = new Worker("./compiler/worker.mjs", {type: "module"});
        } catch (error) {
            failed("Cannot start the compiler: " + error.message);
            return;
        }
        worker.onerror = function (event) {
            failed("Compiler worker failed: " + (event.message || "check your connection and retry."));
        };
        worker.onmessage = function (event) {
            var data = event.data;
            clearTimeout(timer);
            if (data.type === "fatal") {
                failed(data.error);
                return;
            }
            compile.disabled = false;
            compile.textContent = "Compile";
            if (data.type === "ready") {
                ready = true;
                report("Ready. Compilation runs in your browser; source is not uploaded.");
                return;
            }
            pending = false;
            if (compilingRevision !== revision) {
                report("Source changed during compilation. Compile again to update the output.");
            } else if (data.error) {
                report(data.error, true);
            } else {
                output.setValue(data.assembly, -1);
                download.disabled = false;
                report("Compiled successfully. Download the assembly to run it in MARS.");
            }
        };
    }

    source.on("change", function () {
        revision++;
        output.setValue("", -1);
        download.disabled = true;
        if (ready && !pending) report("Source changed. Compile to update the output.");
    });
    compile.addEventListener("click", function () {
        if (!ready) {
            start();
            return;
        }
        var text = source.getValue();
        output.setValue("", -1);
        download.disabled = true;
        if (text.length > 50000) {
            report("Source exceeds the 50,000-character limit.", true);
            return;
        }
        pending = true;
        compilingRevision = revision;
        compile.disabled = true;
        report("Compiling...");
        timer = setTimeout(function () {
            failed("Compilation timed out. Simplify the program and retry.");
        }, 15000);
        worker.postMessage({type: "compile", source: text});
    });
    download.addEventListener("click", function () {
        var url = URL.createObjectURL(new Blob([output.getValue()], {type: "text/plain"}));
        var link = document.createElement("a");
        link.href = url;
        link.download = "program.asm";
        document.body.appendChild(link);
        link.click();
        link.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    });
    window.addEventListener("pagehide", function () {
        clearTimeout(timer);
        if (worker) worker.terminate();
    });
    window.addEventListener("pageshow", function (event) {
        if (event.persisted) {
            ready = false;
            pending = false;
            output.setValue("", -1);
            download.disabled = true;
            start();
        }
    });
    start();
}
