import * as fs from './fsExtra';
import * as vscode from 'vscode';


export function getProjectRoot(): vscode.Uri {
    const workspaces = vscode.workspace.workspaceFolders ?? [];
    if (workspaces.length === 0) {
        return vscode.Uri.parse(process.cwd());
    }

    if (workspaces.length === 1) {
        return workspaces[0].uri;
    }

    let root = workspaces[0].uri;

    for (const w of workspaces) {
        if (root.fsPath.length > w.uri.fsPath.length && fs.exists(w.uri.fsPath)) {
            root = w.uri;
        }
    }

    return root;
}


export function getSelectedRange(editor: vscode.TextEditor): vscode.Range {
    let range = new vscode.Range(editor.selection.start, editor.selection.end);

    if (range.isEmpty) {
        range = editor.document.getWordRangeAtPosition(editor.selection.active) ?? range;
    }

    return range;
}


export async function getSelectedText(editor: vscode.TextEditor): Promise<string | undefined> {
    let range = getSelectedRange(editor);

    if (range.isEmpty) {
        return await vscode.window.showInputBox({ placeHolder: 'Text' });
    }

    return editor.document.getText(range);
}