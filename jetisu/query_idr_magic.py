from IPython.display import display, Markdown, Latex
from jetisu.idr_query import idr_query
import hashlib
def query_idr(line, cell):
    display(Markdown(idr_query(cell, False)))
def query_test(line, cell):
    print("""def test_idr_"""+hashlib.sha1(cell.strip().encode()).hexdigest()[:10]+"""():
    res = idr_query(\"\"\""""+cell+"""\"\"\", True)
    assert sorted_res(res) == sorted_res("""+str(idr_query(cell, True))+""")""")
def show_idr(line, cell):
    with open('jetisu/'+cell.strip().lower() + '.mzn', 'r') as file:
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
    ipython.register_magic_function(query_test, 'cell')