import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand('cloacal.format', () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            return;
        }

        const document = editor.document;
        if (document.languageId !== 'cloacal') {
            return;
        }

        const text = document.getText();
        
        // Spawn Python formatter process
        const { spawn } = require('child_process');
        const { join } = require('path');
        const formatterPath = join(context.extensionPath, 'cloacal_parser.py');
        const config = vscode.workspace.getConfiguration('cloacal');
        const maxLineWidth = config.get('maxLineWidth', 44);
        const pythonProcess = spawn('python3', [formatterPath, '--width', maxLineWidth.toString()]);
        
        let formattedOutput = '';
        let errorOutput = '';

        // Send document text to Python process
        pythonProcess.stdin.write(text);
        pythonProcess.stdin.end();

        // Collect formatted output
        pythonProcess.stdout.on('data', (data: Buffer) => {
            formattedOutput += data.toString();
        });

        pythonProcess.stderr.on('data', (data: Buffer) => {
            errorOutput += data.toString();
        });

        pythonProcess.on('close', (code: number | null) => {
            if (code !== 0) {
                vscode.window.showErrorMessage(`Formatter failed: ${errorOutput}`);
                return;
            }

            editor.edit(editBuilder => {
                const fullRange = new vscode.Range(
                    document.positionAt(0),
                    document.positionAt(text.length)
                );
                editBuilder.replace(fullRange, formattedOutput.trim());
            });
        });
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
