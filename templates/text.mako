---
outline: [2,3]
---

<%
  import os
  import pdoc
  import re
  import textwrap
  import inspect
  import tomllib

  with open('pyproject.toml', 'rb') as _f:
    _project_version = tomllib.load(_f)['project']['version']

  def convert_to_sentence(text):
    # First, handle snake_case by replacing underscores with spaces
    text = text.replace('_', ' ')
    
    # Capitalize the first letter
    text = text[0].upper() + text[1:]
    
    # Handle camelCase by adding spaces before capital letters
    result = ''
    for i, char in enumerate(text):
        if i > 0 and char.isupper():
            result += ' ' + char
        else:
            result += char
            
    return result

  def firstline(ds):
    return ds.split('\n\n', 1)[0]

  def link(dobj, name=None):
    parts = dobj.qualname.split('.')

    if name is None:
      display = parts[-1]
      if isinstance(dobj, pdoc.Function):
        display += '()'
    else:
      display = name

    # External types (not from opengradient) - render as plain code
    if len(parts) >= 2 and parts[0] != 'opengradient':
      return '`{}`'.format(display)

    if len(parts) < 2:
      return '`{}`'.format(display)

    module = parts[1]

    # 3+ parts: submodule or nested object within a submodule
    if len(parts) > 2:
      target = parts[2]
      return '[{}](./{})'.format(display, target)

    # 2 parts: top-level module/package reference
    if isinstance(dobj, pdoc.Module) and dobj.is_package:
      return '[**{}**](./{}/index)'.format(display, module)
    return '[**{}**](./{})'.format(display, module)

  def get_annotation(bound_method, sep=':'):
    annot = show_type_annotations and bound_method() or ''
    if annot:
        annot = ' ' + sep + '\N{NBSP}' + annot
    return annot

  def header(text, level):
    hashes = '#' * level
    return '\n{} {}'.format(hashes, text)

  def breakdown_google(text):
    """
    Break down Google-style docstring format.
    """
    def get_terms(body):
      breakdown = re.compile(r'\n+\s+(\S+):\s+', re.MULTILINE).split('\n' + body)

      # first match is blank (or could be section name if it was still there)
      return list(map(lambda x: textwrap.dedent(x), breakdown[1:]))

    # what we want to do is return the body, before any of the below is
    # matched, and then a list of sections and their terms
    matches = re.compile(r'([A-Z]\w+):$\n', re.MULTILINE).split(inspect.cleandoc(text))
    if not matches:
      return
    body = textwrap.dedent(matches[0].strip())
    sections = {}
    for i in range(1, len(matches), 2):
      title = matches[i].title()
      section = matches[i+1]
      if title in ('Args', 'Attributes', 'Raises'):
        sections[title] = get_terms(section)
      else:
        sections[title] = textwrap.dedent(section)
    return (body, sections)

  def format_for_list(docstring, depth=1):
    spaces = depth * 2 * ' '
    return re.compile(r'\n\n', re.MULTILINE).sub('\n\n' + spaces, docstring)
%>

<%def name="show_breakdown(breakdown)">
  <%
    body = breakdown[0]
    sections = breakdown[1]
    def docsection(text):
      return "**{}**\n\n".format(text)
  %>
${body}
  <%def name="show_args(args)">
    % for i in range(0, len(args), 2):
* **`${args[i]}`**: ${args[i+1]}
    % endfor
  </%def>

  % if sections.get('Args', None):
${docsection('Arguments')}
${show_args(sections['Args'])}
  % endif
  % if sections.get('Attributes', None):
${docsection('Attributes')}
${show_args(sections['Attributes'])}
  % endif
  % if sections.get('Returns', None):
${docsection('Returns')}
${sections['Returns']}
  % endif
  % if sections.get('Raises', None):
${docsection('Raises')}
${show_args(sections['Raises'])}
  % endif
  % if sections.get('Note', None):
${docsection('Note')}
${sections['Note']}
  % endif
  % if sections.get('Notes', None):
${docsection('Notes')}
${sections['Notes']}
  % endif
</%def>

<%def name="show_desc(d, short=False)">
  <%
  inherits = ' inherited' if d.inherits else ''
  #docstring = firstline(d.docstring) if short or inherits else breakdown_google(d.docstring)
  %>
  % if d.inherits:
    _Inherited from:_
    % if hasattr(d.inherits, 'cls'):
`${link(d.inherits.cls)}`.`${link(d.inherits, d.name)}`
    % else:
`${link(d.inherits)}`
    % endif
  % endif
% if short or inherits:
${firstline(d.docstring)}
% else:
${show_breakdown(breakdown_google(d.docstring))}
% endif
</%def>

<%def name="show_list(items, indent=1)">
  <%
    spaces = '  ' * indent
  %>
  % for item in items:
${spaces}* ${link(item, item.name)}
  % endfor
</%def>

<%def name="show_func(f, qual='')">
  <%
    params = ', '.join(f.params(annotate=show_type_annotations))
    return_type = get_annotation(f.return_annotation, '\N{non-breaking hyphen}>')
    qual = qual + ' ' if qual else ''
  %>
${header(convert_to_sentence(f.name), 3)} 

```python
${f.funcdef()} ${f.name}(${params})${return_type}
```
${show_desc(f)}
</%def>

<%def name="show_funcs(fs, qual='')">
  % for f in fs:
${show_func(f, qual)}
  % endfor
</%def>

<%def name="show_vars(vs, qual='')">
  <%
    qual = qual + ' ' if qual else ''
  %>
  % for v in vs:
    <%
      return_type = get_annotation(v.type_annotation)
      return_type_d = ' ' + return_type if return_type else ''
      desc = ' - ' + format_for_list(v.docstring, 1) if v.docstring else ''
    %>
* ${qual}`${v.name}${return_type_d}`${desc}
  % endfor
</%def>

<%def name="show_module(module)">
  <%
  variables = module.variables(sort=sort_identifiers)
  classes = module.classes(sort=sort_identifiers)
  functions = module.functions(sort=sort_identifiers)
  submodules = module.submodules()
  %>

  ## # ${'Namespace' if module.is_namespace else  \
  ##                     'Package' if module.is_package and not module.supermodule else \
  ##                    'Module'} <code>${module.name}</code></h1>

${header('Package ' + module.name, 1)}
% if not module.supermodule:

**Version: ${_project_version}**
% endif

${module.docstring}

%if submodules or variables or functions:

  % if submodules:
${header('Submodules', 2)}

  % for m in submodules:
* ${link(m)}: ${firstline(m.docstring)}
  % endfor
  % endif

  % if functions:
${header('Functions', 2)}

${show_funcs(functions)}
  % endif
% endif

  % if variables:
${header('Global variables', 2)}
${show_vars(variables)}
  % endif

  % if classes:
${header('Classes', 2)}
  % for c in classes:
    <%
    class_vars = c.class_variables(show_inherited_members, sort=sort_identifiers)
    smethods = c.functions(show_inherited_members, sort=sort_identifiers)
    inst_vars = c.instance_variables(show_inherited_members, sort=sort_identifiers)
    methods = c.methods(show_inherited_members, sort=sort_identifiers)
    mro = c.mro()
    subclasses = c.subclasses()
    params = ', '.join(c.params(annotate=show_type_annotations, link=link))
    %>
${header('', 3)} ${c.name}

<code>class <b>${c.name}</b>(${params})</code>

${show_desc(c)}
    % if subclasses:
${header('Subclasses', 4)}
      % for sub in subclasses:
  * ${link(sub)}
      % endfor
    % endif
    % if smethods:
## ${header('Static methods', 4)}
${show_funcs(smethods, 'static')}
    % endif
    % if methods:
## ${header('Methods', 4)}
${show_funcs(methods)}
    % endif
    % if class_vars or inst_vars:
${header('Variables', 4)}
      % if class_vars:
${show_vars(class_vars, 'static')}
      % endif
      % if inst_vars:
${show_vars(inst_vars)}
      % endif
    % endif
    % if not show_inherited_members:
      <%
        members = c.inherited_members()
      %>
      % if members:
${header('Inherited members', 4)}
        % for cls, mems in members:
* `${link(cls)}`:
            % for m in mems:
  * `${link(m, name=m.name)}`
            % endfor
        % endfor
      % endif
    % endif
  % endfor
  % endif
</%def>

${show_module(module)}