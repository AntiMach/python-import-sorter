type StateType = "find" | "file_format" | "file_error" | "done" | "error";

interface StateLog {
    state: StateType;
    file?: string;
    error?: string;
}

interface StateReport {
    message: string;
    increment?: number;
    error?: boolean;
}

export class StateLogHandler {
    constructor(
        private stderr: string = "",
        private filesTotal: number = 0,
        private fileFormats: number = 0,
        private fileErrors: number = 0
    ) { }

    *iterStates(chunk: string): Generator<StateReport> {
        this.stderr += chunk;
        const lines = this.stderr.split("\n");
        this.stderr = lines.pop()!;

        for (const line of lines) {
            try {
                yield this.matchState(JSON.parse(line));
            } catch {
                yield { message: `Non JSON line: ${line}` };
            }
        }
    }

    getResult() {
        return { fileFormats: this.fileFormats, fileErrors: this.fileErrors };
    }

    private matchState({ state, file, error }: StateLog): StateReport {
        switch (state) {
            case "find":
                this.filesTotal += 1;
                return { message: `Found ${file}.` };

            case "file_format":
                this.fileFormats += 1;
                return { message: `Processed ${file}.`, increment: this.increment };

            case "file_error":
                this.fileErrors += 1;
                return { message: `File ${file} encountered errors: ${error}`, increment: this.increment, error: true };

            case "done":
                return { message: "Completed." };

            case "error":
                return { message: error!, error: true };

            default:
                return { message: "Unknown state." };
        }
    }

    private get increment(): number {
        return this.filesTotal > 0 ? 100 / this.filesTotal : 0;
    }
}
