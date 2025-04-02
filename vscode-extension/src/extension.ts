import * as vscode from "vscode";
import * as path from "path";
import { exec } from "child_process";

const EXTENSION_NAME = "python-import-sorter";

const EXTENSION_ROOT_DIR = path.dirname(__dirname);
const SCRIPT_PATH = path.join(EXTENSION_ROOT_DIR, "bundled", "tool", "script.py");

async function getPythonPath(): Promise<string> {
    const extension = vscode.extensions.getExtension("ms-python.python");
    if (!extension) {
        return "python";
    }

    if (!extension.isActive) {
        await extension.activate();
    }

    const pythonPath = extension.exports.settings.getExecutionDetails().execCommand?.[0];
    return pythonPath || "python";
}

function getFormatter(): string | undefined {
    return vscode.workspace.getConfiguration(EXTENSION_NAME).get("formatter");
}

function getGroups(): string[] {
    return vscode.workspace.getConfiguration(EXTENSION_NAME).get("groups") ?? [];
}

async function getFullCommand(): Promise<string> {
    const pythonPath = await getPythonPath();
    let fullCommand = `"${pythonPath}" "${SCRIPT_PATH}" -`;
    const formatter = getFormatter();
    const groups = getGroups();

    if (formatter !== undefined) {
        fullCommand += ` -f "${formatter}"`;
    }

    if (groups.length > 0) {
        fullCommand += ` -g ${groups.join(" ")}`;
    }

    return fullCommand;
}

export function activate(context: vscode.ExtensionContext) {
    console.log(`"${EXTENSION_NAME}" is now active`);

    const disposable = vscode.languages.registerDocumentFormattingEditProvider(
        { scheme: "file", language: "python" },
        {
            async provideDocumentFormattingEdits(document: vscode.TextDocument): Promise<vscode.TextEdit[]> {
                const fullRange = new vscode.Range(
                    document.lineAt(0).range.start,
                    document.lineAt(document.lineCount - 1).range.end
                );

                try {
                    const command = await getFullCommand();

                    return new Promise<vscode.TextEdit[]>((resolve, reject) => {
                        const proc = exec(command, {}, (error, stdout, stderr) => {
                            if (error) {
                                vscode.window.showErrorMessage(`Error formatting: ${stderr}`);
                                reject(error);
                                return;
                            }

                            resolve([vscode.TextEdit.replace(fullRange, stdout)]);
                        });

                        if (proc.stdin) {
                            proc.stdin.write(document.getText(fullRange));
                            proc.stdin.end(); // Important: close the stdin stream
                        } else {
                            reject(new Error("Failed to access stdin of the process"));
                        }
                    });
                } catch (error) {
                    return [];
                }
            },
        }
    );

    context.subscriptions.push(disposable);

    const disposable2 = vscode.commands.registerCommand("python-import-sorter.format", () => {
        vscode.window.showInformationMessage("Hello World!");
    });

    context.subscriptions.push(disposable2);
}

export function deactivate() {}
