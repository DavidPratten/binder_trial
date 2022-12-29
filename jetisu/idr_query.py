# !/usr/bin/env python
# coding: utf-8

# Basic imports and setup

# In[535]:
from sqlglot.executor import execute
from sqlglot import exp, parse_one
import subprocess
import json
import os
import tempfile
import sys
import re

def idr_read_model(canonical_table_name):
    with open('jetisu/' + canonical_table_name + '.mzn', 'r') as file:
        return file.read()

def idr_query(SQL, return_data):

    assert return_data in ['data', 'markdown table', 'model', 'constrained model']

    # handles a conjuction of simple constraint clauses only TODO Generalise this code.
    table_name = ''
    where_clause = ''
    column_name = ''
    found_where = False
    found_constraints = False
    found_EQ = False
    found_Not = False
    found_Negated_Boolean = False
    too_complex = False
    eq_constraints = {}

    for node_tuple in parse_one(SQL).walk(bfs=False):
        # print(type(node_tuple[0]), node_tuple[0].name)
        if isinstance(node_tuple[0], exp.Identifier):
            # for current purposes the Identifiers may be ignored.
            # print('ignoring', str(node_tuple[0]))
            continue
        if isinstance(node_tuple[0], exp.Group) or isinstance(node_tuple[0], exp.Having) or isinstance(node_tuple[0],
                                                                                                       exp.Order):
            found_where = False
            found_constraints = False
            continue
        if isinstance(node_tuple[0], exp.Table):
            table_name = str(node_tuple[0])
            continue
        if isinstance(node_tuple[0], exp.Where):
            where_clause = str(node_tuple[0])
            found_where = True
            continue
        if found_where:
            if isinstance(node_tuple[0], exp.And):
                continue
            elif isinstance(node_tuple[0], exp.EQ) or isinstance(node_tuple[0], exp.Not) or isinstance(node_tuple[0],
                                                                                                       exp.Column):
                found_where = False
                found_constraints = True
            else:
                too_complex = True
                continue
        if found_constraints and not found_EQ and not found_Not:
            if isinstance(node_tuple[0], exp.EQ):
                found_EQ = True
                continue
            if isinstance(node_tuple[0], exp.Not):
                found_Not = True
                continue
            if isinstance(node_tuple[0], exp.Column):
                eq_constraints[str(node_tuple[0]).lower()] = True
                continue
            too_complex = True
            continue
        if found_constraints and found_EQ and column_name == '':
            if isinstance(node_tuple[0], exp.Column):
                column_name = str(node_tuple[0]).lower()
                continue
            too_complex = True
            continue
        if found_constraints and found_EQ and column_name != '':
            if isinstance(node_tuple[0], exp.Literal):
                # print(node_tuple[0].is_string, str(node_tuple[0]))

                eq_constraints[column_name] = str(node_tuple[0]) if node_tuple[0].is_string else float(
                    str(node_tuple[0]))
                found_EQ = False
                column_name = ''
                continue
            too_complex = True
            continue
        if found_constraints and found_Not:
            if isinstance(node_tuple[0], exp.Column):
                eq_constraints[str(node_tuple[0]).lower()] = False
                found_Not = False
                continue
            too_complex = True
            continue

    # print('table', table_name)
    # print(where_clause)
    # print(eq_constraints)
    # print(too_complex)

    # In[538]:
    canonical_table_name = table_name.lower()
    model = idr_read_model(canonical_table_name)

    # print(model)

    # Merge in the constraints in the query to get the model to be fed to MiniZinc

    parameters = re.search("predicate +" + canonical_table_name + " *\(([^\)]+?)\)", model, re.S)[1].lower()
    variables = parameters.replace(",", ";") + ";"
    primary_constraint = 'constraint ' + canonical_table_name + '(' + ', '.join(
        [x.split(":")[1] for x in parameters.split(",")]) + ');'

    # print(variables)
    # print(primary_constraint)

    where_clause_data = '; '.join([(x + "= true" if len(x.split("=")) == 1 else x) for x in
                                   where_clause.lower().replace("where", "").split("and")])
    # print(where_clause_list)
    constrained_model = model + "\n" + variables + "\n" + primary_constraint + "\n" + where_clause_data + ";"
    # print(model)
    model_fn = tempfile.NamedTemporaryFile().name
    mf = open(model_fn + ".mzn", 'w')
    mf.write(constrained_model)
    mf.close()

    # print (model)

    # Run MiniZinc model and save result

    # In[541]:

    path_to_minizinc = "C:/Program Files/MiniZinc/minizinc" if sys.platform.startswith('win32') else "/usr/bin/minizinc"
    additional_calling_parameters = [] if sys.platform.startswith('win32') else ["-input", "fzn",
                                                                                 "-opt.fzn.all_solutions", "true",
                                                                                 "-opt.fzn.finite_precision", "12",
                                                                                 "-opt.fzn.finite_precision_model",
                                                                                 "true"]
    # path_to_optimathsat = "C:/Program Files/MiniZinc/bin/optimathsat" if sys.platform.startswith(
    #     'win32') else "/usr/bin/optimathsat"
    # print(constrained_model)
    result = subprocess.run(
        [path_to_minizinc, "--solver", "optimathsat"] + additional_calling_parameters + [model_fn + ".mzn"],
        stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    # print('here', output)
    #sys.exit(0)
    # In[542]:

    # result = subprocess.run(["C:\Program Files\MiniZinc\minizinc.exe", "-c", model_fn], stdout=subprocess.PIPE)
    # print(result.stdout.decode('utf-8'))

    # result = subprocess.run(
    #     [path_to_optimathsat, "-input=fzn", "-opt.fzn.max_solutions=1000",
    #      "-opt.fzn.finite_precision=12", "-opt.fzn.finite_precision_model=true",
    #      "-opt.fzn.all_solutions=true", "-opt.fzn.output_var_file=-", "-model_generation=true",
    #      model_fn + ".fzn"],
    #     stdout=subprocess.PIPE)  # "-opt.fzn.output_var_file="+model_fn+"_vars.txt",
    # output = result.stdout.decode('utf-8')
    # print(output)

    # In[543]:

    data_output = []
    data = False
    column = []
    for line in output.splitlines():
        if not data:
            if line == "% allsat model":
                data = True
        if data:
            if line == "% allsat model":
                column = []
            elif line == "----------":

                data_output.append('{' + ', '.join(column) + '}')
            elif line == "==========":
                pass
            else:
                x = line.replace(";", "").split("=")
                column.append('"' + x[0].strip() + '": ' + x[1].strip())
    solver_data = json.loads('[' + ', '.join(data_output) + ']')
    # print(solver_data)

    # In[544]:

    # clean up TODO Complete the cleanup
    os.remove(model_fn + ".mzn")
    # os.remove(model_fn + ".ozn")
    # os.remove(model_fn + ".fzn")

    # Put output into a list of dict as data ready to run

    # In[545]:

    table_input = {table_name.lower(): [x | eq_constraints for x in solver_data]}  # | eq_constraints
    # print(eq_constraints)
    # print(table_input)

    # Run the query

    # In[546]:

    # print (SQL)
    res = execute(
        SQL,
        tables=table_input
    )

    # In[547]:

    # short_input = {'act_conveyance_duty': table_input['act_conveyance_duty'][:4]}
    # SQLtest = """select
    #     product_name,
    #     min(price) min_price
    # from products
    # group by product_name
    #     ;"""
    # res = execute(
    #     """select product_name, imported,  min(price) min_price from products group by product_name, imported;""",
    #     tables={'products':[{'product_name': 'Bike', 'price': 100, 'imported': True},{'product_name': 'Tent', 'price': 200, 'imported': True},{'product_name': 'Bike', 'price': 300,  'imported': False}]}
    # )
    if return_data == 'data':
        return (res.columns, res.rows)
    elif return_data == 'markdown table':
        return '|' + '|'.join(res.columns) + '|' + "\n" + '|' + '|'.join(
            ["----" for x in res.columns]) + '|' + "\n" + "\n".join(
            ['|' + '|'.join([str(val) for val in r]) + '|' for r in res.rows])
    elif return_data == 'model':
        return model
    elif return_data == 'constrained model':
        return constrained_model
    else:
        return 'Programming error this should never occur'
    # print(res.columns)
    # print()

    # print(table_mkdn)
    # print(res.columns)
    # for i in res.rows:
    #     print(i)
    #     for j in i:
    #         print (j)

    # Present the output.
