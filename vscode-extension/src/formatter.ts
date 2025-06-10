import * as vscode from "vscode";
import * as fs from "fs";
import { spawn } from "child_process";

import * as config from "./config";
import * as result from "./result";
import { Result } from "./result";
import { StateLogHandler } from "./logParser";
import { PythonExtension } from "@vscode/python-extension";

interface ScriptOptions {
    files?: string[];
    content?: string;
    strict?: boolean;
    progress?: vscode.Progress<{ message?: string; increment?: number }>;
    token?: vscode.CancellationToken;
}

type ScriptResult = Result<{ stdout: string; fileFormats: number; fileErrors: number }, string>;

export class Formatter {
    logger: vscode.OutputChannel;

    SHOW_LOGS = "Show logs";

    constructor() {
        this.logger = vscode.window.createOutputChannel(config.EXTENSION_DISPLAY_NAME);
    }

    init(context: vscode.ExtensionContext) {
        context.subscriptions.push(
            vscode.commands.registerTextEditorCommand(config.extKey("formatDocument"), this.formatDocument.bind(this)),
            vscode.commands.registerCommand(config.extKey("formatAllDocuments"), this.formatBulkDocuments.bind(this)),
            vscode.languages.registerDocumentRangeFormattingEditProvider(
                { scheme: "file", language: "python" },
                { provideDocumentRangeFormattingEdits: this.formatSingleDocument.bind(this) }
            )
        );
    }

    private async formatDocument(textEditor: vscode.TextEditor, textEdit: vscode.TextEditorEdit) {
        const edits = await this.formatSingleDocument(textEditor.document);
        if (!edits) return;

        for (const edit of edits) textEdit.replace(edit.range, edit.newText);
    }

    private async formatSingleDocument(
        document: vscode.TextDocument,
        range?: vscode.Range
    ): Promise<vscode.TextEdit[]> {
        if (range === undefined || range.isEmpty) {
            range = new vscode.Range(document.lineAt(0).range.start, document.lineAt(document.lineCount - 1).range.end);
        }

        const { ok, value } = await this.runScript({ content: document.getText(range), strict: true });

        if (ok) return [vscode.TextEdit.replace(range, value.stdout)];

        this.logger.appendLine(value);
        vscode.window
            .showErrorMessage(`Failed to format file:\n${value}`, this.SHOW_LOGS)
            .then((s) => this.showLogsButton(s));
        return [];
    }

    private async formatBulkDocuments() {
        const filesString = await vscode.window.showInputBox({
            prompt: "Enter a list of files to format (folders and globs allowed) separated by commas",
            placeHolder: "e.g., src/**/*.py main.py",
        });

        if (filesString === undefined) return;

        const files = filesString
            .split(",")
            .map((v) => v.trim())
            .filter((v) => v !== "");

        const { ok, value } = await this.runScriptWithProgress({ files });

        if (!ok) {
            this.logger.appendLine(value);
            vscode.window.showErrorMessage(value, this.SHOW_LOGS).then((s) => this.showLogsButton(s));
            return;
        }

        const { fileFormats, fileErrors } = value;

        let message = "";

        if (fileFormats > 0) message += `Successfully formatted ${fileFormats} files.\n`;
        if (fileErrors > 0) message += `Failed to format ${fileErrors} files.\n`;

        this.logger.appendLine(message);
        vscode.window.showInformationMessage(message, this.SHOW_LOGS).then((s) => this.showLogsButton(s));
    }

    private showLogsButton(selection?: string) {
        if (selection === this.SHOW_LOGS) this.logger.show(true);
    }

    private async runScriptWithProgress({ files, content }: ScriptOptions): Promise<ScriptResult> {
        return vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: "Sorting files",
                cancellable: true,
            },
            (progress, token) => this.runScript({ files, content, progress, token })
        );
    }

    private async runScript({ files, content, strict, progress, token }: ScriptOptions): Promise<ScriptResult> {
        // Current working directory
        const cwd = this.getProjectRoot();

        // Bundled script
        let args = [await this.currentPythonExecutable(), config.SCRIPT_PATH];

        // Files
        if (files) args.push(...files);
        else args.push("-");

        // Flags
        const { format, groups, configPath, exclude } = config.settings();

        if (format) args.push("-f", format);
        if (groups.length > 0) args.push("-g", ...groups);
        if (configPath) args.push("-c", configPath);
        if (exclude.length > 0) args.push("-x", ...exclude);

        // Output in json format
        args.push("-j");

        return new Promise((resolve) => {
            const process = spawn(args[0], args.slice(1), { cwd });
            const stateHandler = new StateLogHandler();
            let stdout = "";

            // Output channels encoding settings
            process.stdout.setEncoding("utf8");
            process.stderr.setEncoding("utf8");

            // Output channels data handling
            process.stdout.on("data", (chunk) => (stdout += chunk));
            process.stderr.on("data", (chunk) => {
                for (const { message, increment, error } of stateHandler.iterStates(chunk)) {
                    if (progress) progress.report({ message, increment });
                    this.logger.appendLine(message);
                    if (strict && error) resolve(result.err(message));
                }
            });

            // Occurs when the process fails to run
            process.on("error", (err) => resolve(result.err(err.message)));

            // Occurs when the process ends
            process.on("close", (code) => {
                if (code === 0) resolve(result.ok({ stdout, ...stateHandler.getResult() }));
                else resolve(result.err(`Process exited with code ${code}`));
            });

            // Writes the provided contents to stdin and closes it
            if (content) process.stdin.end(content);
            if (token) token.onCancellationRequested(() => process.kill());
        });
    }

    //#region Helpers

    private getProjectRoot(): string {
        const workspaces = vscode.workspace.workspaceFolders ?? [];

        if (workspaces.length === 0) return process.cwd();

        return workspaces.reduce(
            (shortest, w) =>
                shortest.length > w.uri.fsPath.length && this.fileExists(w.uri.fsPath) ? w.uri.fsPath : shortest,
            workspaces[0].uri.fsPath
        );
    }

    private fileExists(path: string): boolean {
        try {
            fs.statSync(path);
            return true;
        } catch {
            return false;
        }
    }

    private async currentPythonExecutable() {
        const pythonApi = await PythonExtension.api();
        const environments = pythonApi.environments;
        const environment = await environments.resolveEnvironment(environments.getActiveEnvironmentPath());
        const result = environment?.executable.uri?.fsPath;

        if (result === undefined) throw new Error("No active python environment found");

        return result;
    }

    //#endregion
}
