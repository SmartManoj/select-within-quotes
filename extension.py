import vscode
from vscode import InfoMessage

ext = vscode.Extension("Select Text Within Quotes")

@ext.event
async def on_activate():
    vscode.log(f"The Extension '{ext.name}' has started")

import re
from vscode import window, Range, Position

@ext.command()
async def select_text_within_quotes(ctx):
    # Access the active text editor
    try:
        editor = await ctx.window.active_text_editor
        if not editor:
            return await ctx.show(InfoMessage("No active text editor found"))

        # Get the current selection or cursor position
        selection = editor.selection
        start = selection.start
        
        start_line = Position(start.line, 0)
        backward_text = await editor.document.get_text(Range(start_line, start))
        forward_text = await editor.document.get_text(Range(start, Position(start.line+1,0 )))
        vscode.log(f"backward_text: {backward_text}")
        vscode.log(f"forward_text: {forward_text}")
        # Regular expression to find text within quotes
        # Adjust the regex according to the types of quotes you want to handle
        # backward_text find `,',",""" from last occurance
        start_pos = end_pos = -1
        three_quotes = ['"""',"'''"]
        quotes_list = ['"""','"','\'','`',"'''"]
        # Search in backward_text in reverse
        for k in reversed(range(len(backward_text))):
            i = backward_text[k]
            if i in quotes_list:
                start_pos = k
                if i in three_quotes and backward_text[k-1] != '\\':
                    # Adjust the position for triple quotes
                    start_pos -= 2  # Using '-=' since we are iterating in reverse

                # Check for the quote's position in forward_text
                end_pos = forward_text.find(i)
                if end_pos != -1 and forward_text[end_pos-1] != '\\':
                    # Found the corresponding quote in forward_text
                    break
                # If not found, continue searching
        
        

        if end_pos != -1:
            # Calculate the new selection range (excluding the quotes)
            new_start = Position(start.line, start_pos+1)
            new_end = Position(start.line, start.character+end_pos)
            new_selection = Range(new_start, new_end)

            # Update the selection in the editor
            editor.selection = new_selection
            s,e = new_selection.start, new_selection.end
            code = f'''
            let editor = vscode.window.activeTextEditor;
            editor.selections = editor.selections.map(sel => new vscode.Selection(
                new vscode.Position({s.line}, {s.character}), 
                new vscode.Position({e.line}, {e.character})
            ));

            '''
            await ctx.ws.run_code(code, thenable=False)
    except Exception as e:
        await ctx.show(InfoMessage(f"Error: {e}"))
        raise e


ext.run()

# test cases
"""dfdfdf"""
# regenerate_buttons = (By.XPATH, "//div[preceding-sibling::*[1][self::button] and contains(@class, 'flex') and contains(@class, 'gap-1') and count(button)=2]")
