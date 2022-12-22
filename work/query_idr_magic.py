from IPython.display import display, Markdown, Latex
from work.idr_query import idr_query
def query_idr(line, cell):
    display(Markdown(idr_query(cell, False)))
def show_idr(line, cell):
    with open('work/'+cell.strip().lower() + '.mzn', 'r') as file:
        model = file.read()
    display(Markdown("```\n\n"+model+"\n```"))
def load_ipython_extension(ipython):
    """This function is called when the extension is
    loaded. It accepts an IPython InteractiveShell
    instance. We can register the magic with the
    `register_magic_function` method of the shell
    instance."""
    ipython.register_magic_function(query_idr, 'cell')
    ipython.register_magic_function(show_idr, 'cell')