import * as path from "path";
import * as vscode from "vscode";
import * as pkg from "../package.json";

export const EXTENSION_NAME = pkg.name;
export const EXTENSION_DISPLAY_NAME = pkg.displayName;

export const EXTENSION_ROOT_DIR =
    path.basename(__dirname) === "common" ? path.dirname(path.dirname(__dirname)) : path.dirname(__dirname);

export const SCRIPT_PATH = path.join(EXTENSION_ROOT_DIR, "bundled", "tool", "script.py");

export interface Settings {
    format: string | undefined;
    groups: string[];
    configPath: string | undefined;
    exclude: string[];
}

export function settings(): Settings {
    const config = vscode.workspace.getConfiguration(EXTENSION_NAME);
    return {
        format: config.get("format") ?? undefined,
        groups: config.get("groups") ?? [],
        configPath: config.get("config") ?? undefined,
        exclude: config.get("exclude") ?? [],
    };
}

export function extKey(name: string): string {
    return `${EXTENSION_NAME}.${name}`;
}
