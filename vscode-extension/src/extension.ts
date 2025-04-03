import * as vscode from "vscode";
import * as config from "./common/config";
import * as python from "./common/pythonEnvsApi";

async function runScript(content: string): Promise<string> {
    const api = await python.getEnvExtApi();
    const env = await api.getEnvironment(undefined);

    if (!env) {
        throw new Error("No active environment found");
    }

    let args = [config.SCRIPT_PATH, "-"];
    const { format, groups } = config.settings();

    if (format) {
        args.push("-f", format);
    }

    if (groups.length > 0) {
        args.push("-g", ...groups);
    }

    const proc = await api.runInBackground(env, { args });

    proc.stdin.write(content);
    proc.stdin.end();

    return new Promise((resolve, reject) => {
        proc.onExit((code) => {
            if (code === 0) {
                return resolve(proc.stdout.read().toString());
            }
            reject(new Error(proc.stderr.read().toString()));
        });
    });
}

export function activate(context: vscode.ExtensionContext) {
    const formatter = vscode.languages.registerDocumentFormattingEditProvider(
        { scheme: "file", language: "python" },
        {
            async provideDocumentFormattingEdits(document: vscode.TextDocument): Promise<vscode.TextEdit[]> {
                const fullRange = new vscode.Range(
                    document.lineAt(0).range.start,
                    document.lineAt(document.lineCount - 1).range.end
                );

                try {
                    const result = await runScript(document.getText(fullRange));
                    return [vscode.TextEdit.replace(fullRange, result)];
                } catch (error) {
                    vscode.window.showErrorMessage("Failed to format file");
                    return [];
                }
            },
        }
    );

    const command = vscode.commands.registerCommand("python-import-sorter.format", () => { });

    context.subscriptions.push(formatter, command);
}

export function deactivate() { }
