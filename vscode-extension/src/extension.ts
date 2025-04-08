import { ExtensionContext } from "vscode";
import { Formatter } from "./formatter";



export function activate(context: ExtensionContext) {
    (new Formatter()).init(context);
}

export function deactivate() { }
