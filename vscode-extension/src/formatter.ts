import * as vscode from "vscode";
import * as vsapi from './common/vsapi';
import * as config from "./common/config";
import * as python from "./common/pythonEnvsApi";


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

        context.subscriptions.push(vscode.languages.registerDocumentRangeFormattingEditProvider(
            { scheme: "file", language: "python" },
            { provideDocumentRangeFormattingEdits: this.format.bind(this) }
        ))
    }

    async formatDocument(textEditor: vscode.TextEditor, textEdit: vscode.TextEditorEdit) {
        const edits = await this.format(textEditor.document, undefined);

        for (const edit of edits) {
            textEdit.replace(edit.range, edit.newText);
        }
    }

    async format(document: vscode.TextDocument, range: vscode.Range | undefined): Promise<vscode.TextEdit[]> {
        if (range === undefined || range.isEmpty) {
            range = new vscode.Range(
                document.lineAt(0).range.start,
                document.lineAt(document.lineCount - 1).range.end
            );
        }

        try {
            const result = await this.runScript(document.getText(range));
            return [vscode.TextEdit.replace(range, result)];
        } catch (error) {
            this.logger.appendLine(this.errorToString(error));
            return [];
        }
    }

    async runScript(content: string): Promise<string> {
        const api = await python.getEnvExtApi();
        const env = await api.getEnvironment(undefined);

        if (!env) {
            throw new Error("No active environment found");
        }

        let args = [config.SCRIPT_PATH, "-"];
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

        const proc = await api.runInBackground(env, { args, cwd: vsapi.getProjectRoot() });

        proc.stdin.write(content);
        proc.stdin.end();

        return new Promise<string>((resolve, reject) => {
            proc.onExit((code) => {
                if (code === 0) {
                    return resolve(proc.stdout.read().toString());
                }
                reject(new Error(proc.stderr.read().toString()));
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