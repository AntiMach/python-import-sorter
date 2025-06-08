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
        const projectRoot = vsapi.getProjectRoot().fsPath;

        return vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Formatting Python Files",
            cancellable: true
        }, async (progress, token) => {
            try {
                const pythonFiles = await vscode.workspace.findFiles(`${projectRoot}/**/*.py`, `${projectRoot}/**/.venv/*.py`);

                if (pythonFiles.length === 0) {
                    vscode.window.showInformationMessage("No Python files found in workspace");
                    return;
                }

                progress.report({ message: `Found ${pythonFiles.length} Python files` });

                await this.runScript({ files: `${projectRoot}/**/*.py`, excludes: `${projectRoot}/**/.venv/*.py` });

                progress.report({ message: `Done formatting` });

            } catch (error) {
                this.logger.appendLine(this.errorToString(error));
                vscode.window.showErrorMessage(
                    `Failed to format Python files: ${this.errorToString(error)}`
                );
                throw error;
            }
        });
    }

    async format(document: vscode.TextDocument, range?: vscode.Range): Promise<vscode.TextEdit[]> {
        if (range === undefined || range.isEmpty) {
            range = new vscode.Range(
                document.lineAt(0).range.start,
                document.lineAt(document.lineCount - 1).range.end
            );
        }

        try {
            const result = await this.runScript({ content: document.getText(range) });
            return [vscode.TextEdit.replace(range, result)];
        } catch (error) {
            this.logger.appendLine(this.errorToString(error));
            return [];
        }
    }

    async runScript(options: { files?: string, excludes?: string, content?: string }): Promise<string> {
        const projectRoot = vsapi.getProjectRoot();

        const pythonPath = await this.currentPythonExecutable();

        if (pythonPath === undefined) {
            throw new Error("No active environment found");
        }

        let args = [config.SCRIPT_PATH];

        if (options.files) {
            args.push(options.files)
        } else {
            args.push("-")
        }

        if (options.excludes) {
            args.push("-x", options.excludes)
        }

        const { format, groups, configPath } = config.settings();

        if (format) {
            args.push("-f", format);
        }

        if (groups.length > 0) {
            args.push("-g", ...groups);
        }

        if (configPath) {
            args.push("-c", configPath);
        }

        return new Promise<string>((resolve, reject) => {
            const proc = spawn(pythonPath, args, { cwd: projectRoot.fsPath, });

            let stdout = "";
            let stderr = "";

            proc.stdout.setEncoding('utf8');
            proc.stderr.setEncoding('utf8');

            proc.stdout.on('data', chunk => stdout += chunk);
            proc.stderr.on('data', chunk => stderr += chunk);

            proc.on('error', (err) => reject(new Error(err.message)));

            proc.on("close", (code) => {
                if (code === 0) {
                    resolve(stdout);
                } else {
                    reject(new Error(stderr.trim() || `Process exited with code ${code}`));
                }
            });

            if (options.content) {
                proc.stdin.end(options.content);
            }
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