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

        // Basic formatting implementation
        // TODO: Implement actual formatting logic
        const text = document.getText();
        const formatted = text.split('\n').map(line => line.trim()).join('\n');

        editor.edit(editBuilder => {
            const fullRange = new vscode.Range(
                document.positionAt(0),
                document.positionAt(text.length)
            );
            editBuilder.replace(fullRange, formatted);
        });
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
