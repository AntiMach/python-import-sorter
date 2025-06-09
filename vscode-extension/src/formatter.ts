import * as vscode from "vscode";
import * as vsapi from './common/vsapi';
import * as config from "./common/config";

import { spawn } from "child_process";
import { PythonExtension } from '@vscode/python-extension';


export class Formatter {
    logger: vscode.OutputChannel;

    constructor() {
        this.logger = vscode.window.createOutputChannel(config.EXTENSION_DISPLAY_NAME);
    }

    init(context: vscode.ExtensionContext) {
        context.subscriptions.push(vscode.commands.registerTextEditorCommand(
            config.extKey("formatDocument"),
            this.formatDocument.bind(this)
        ))

        context.subscriptions.push(vscode.commands.registerCommand(
            config.extKey("formatAllDocuments"),
            this.formatAllDocuments.bind(this)
        ))

        context.subscriptions.push(vscode.languages.registerDocumentRangeFormattingEditProvider(
            { scheme: "file", language: "python" },
            { provideDocumentRangeFormattingEdits: this.format.bind(this) }
        ))
    }

    async currentPythonExecutable() {
        const pythonApi = await PythonExtension.api();
        const environments = pythonApi.environments;
        const environment = await environments.resolveEnvironment(environments.getActiveEnvironmentPath());
        return environment?.executable.uri?.fsPath;
    }

    async formatDocument(textEditor: vscode.TextEditor, textEdit: vscode.TextEditorEdit) {
        const edits = await this.format(textEditor.document);

        for (const edit of edits) {
            textEdit.replace(edit.range, edit.newText);
        }
    }

    async formatAllDocuments() {
        const filesString = await vscode.window.showInputBox({
            prompt: "Enter a list of files to format (folders and globs allowed) separated by commas",
            placeHolder: "e.g., src/**/*.py main.py"
        });

        if (filesString === undefined) {
            return;
        }

        const files = filesString.split(",").map(v => v.trim()).filter(v => v !== "");

        try {
            const { fileCount, fileErrors } = await this.runScript({ files });
            let message = [];

            if (fileCount > 0) {
                message.push(`Successfully formatted ${fileCount} files.`)
            }

            if (fileErrors > 0) {
                message.push(`Failed to format ${fileErrors} files (check logs).`);
            }

            vscode.window.showInformationMessage(message.join("\n"), "Show Logs").then((selection) => {
                if (selection === "Show Logs") {
                    this.logger.show(true);
                }
            });

        } catch (error) {
            vscode.window.showErrorMessage(`Failed to format files:\n${this.errorToString(error)}`);
            this.logger.appendLine(this.errorToString(error));
            throw error;
        }
    }

    async format(document: vscode.TextDocument, range?: vscode.Range): Promise<vscode.TextEdit[]> {
        if (range === undefined || range.isEmpty) {
            range = new vscode.Range(
                document.lineAt(0).range.start,
                document.lineAt(document.lineCount - 1).range.end
            );
        }

        try {
            const { result } = (await this.runScript({ content: document.getText(range) }));
            return [vscode.TextEdit.replace(range, result)];
        } catch (error) {
            vscode.window.showErrorMessage(`Failed to format file:\n${this.errorToString(error)}`);
            this.logger.appendLine(this.errorToString(error));
            return [];
        }
    }

    async runScript(options: {
        files?: string[],
        content?: string,
    }): Promise<{ result: string, fileCount: number, fileErrors: number }> {
        const projectRoot = vsapi.getProjectRoot();

        const pythonPath = await this.currentPythonExecutable();

        if (pythonPath === undefined) {
            throw new Error("No active environment found");
        }

        let args = [config.SCRIPT_PATH];

        if (options.files) {
            args.push(...options.files)
        } else {
            args.push("-")
        }

        const { format, groups, configPath, exclude } = config.settings();

        if (format) {
            args.push("-f", format);
        }

        if (groups.length > 0) {
            args.push("-g", ...groups);
        }

        if (configPath) {
            args.push("-c", configPath);
        }

        if (exclude.length > 0) {
            args.push("-x", ...exclude)
        }

        args.push("-j")


        return vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Import Sorter",
            cancellable: true,
        }, async (progress, token) => {
            return new Promise((resolve, reject) => {
                const proc = spawn(pythonPath, args, { cwd: projectRoot.fsPath });

                let stdout = "";
                let stderr = "";
                let fileCount = 0;
                let fileErrors = 0;
                let prevProg = 0;

                proc.stdout.setEncoding('utf8');
                proc.stderr.setEncoding('utf8');

                proc.stdout.on('data', chunk => stdout += chunk);

                // Processes log data
                proc.stderr.on('data', chunk => {
                    stderr += chunk;
                    const lines = stderr.split('\n');
                    stderr = lines.pop()!;

                    for (const line of lines) {
                        let json;

                        try {
                            json = JSON.parse(line.trim());
                        } catch (err) {
                            this.logger.appendLine(`Non-JSON stderr: ${line}`);
                            continue;
                        }

                        let message;
                        let increment = 0;

                        switch (json.state) {
                            case "init":
                                message = `Found ${json.file}`;
                                break;
                            case "file":
                                message = `Processed ${json.file}`;
                                fileCount += 1;
                                increment = json.prog - prevProg;
                                prevProg = json.prog;
                                break;
                            case "done":
                                message = `Completed.`;
                                break;
                            case "file_error":
                                message = `File ${json.file} has syntax errors. ${json.error}`;
                                fileErrors += 1;
                                increment = json.prog - prevProg;
                                prevProg = json.prog;
                                break;
                            case "error":
                                message = json.message;
                                return;
                        }

                        if (message !== undefined) {
                            progress.report({ message, increment });
                            this.logger.appendLine(message);
                        }
                    }
                });

                // Occurs when the process fails to run
                proc.on("error", err => reject(new Error(err.message)));

                // Occurs when the process ends
                proc.on("close", code => {
                    if (code === 0) {
                        resolve({ result: stdout, fileCount, fileErrors });
                    } else {
                        reject(new Error(`Process exited with code ${code}`));
                    }
                });

                // Writes the provided contents to stdin and closes it
                if (options.content) {
                    proc.stdin.end(options.content);
                }

                token.onCancellationRequested((e) => {
                    proc.kill();
                })
            });
        });
    }

    //#region Helpers

    private errorToString(error: unknown): string {
        if (error instanceof Error) {
            return error.message;
        }
        if (typeof error === "string") {
            return error;
        }
        try {
            return JSON.stringify(error);
        } catch {
            return String(error);
        }
    }

    //#endregion
}