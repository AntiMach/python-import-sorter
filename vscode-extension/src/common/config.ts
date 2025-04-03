import * as path from "path";
import * as vscode from "vscode";
import * as pkg from "../../package.json";

export const EXTENSION_NAME = pkg.name;

export const EXTENSION_ROOT_DIR =
    path.basename(__dirname) === "common" ? path.dirname(path.dirname(__dirname)) : path.dirname(__dirname);

export const SCRIPT_PATH = path.join(EXTENSION_ROOT_DIR, "bundled", "tool", "script.py");

export interface Settings {
    format: string | undefined;
    groups: string[];
}

export function settings(): Settings {
    return {
        format: vscode.workspace.getConfiguration(EXTENSION_NAME).get("format") ?? undefined,
        groups: vscode.workspace.getConfiguration(EXTENSION_NAME).get("groups") ?? [],
    };
}
