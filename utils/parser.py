
import re
import os
import sys
import collections


class GroovyDocParser(object):

    def __init__(self):
        pass

    @staticmethod
    def parse_file(groovy_file_path):
        # type: (str) -> GroovyFile
        groovy_file_obj = GroovyFile(groovy_file_path)
        return groovy_file_obj


class GroovyFile(object):

    REGEX_GROOVYDOC_FUNCTION = re.compile(r'(/\*\*([^*]|\*(?!/))*?.*?\*/\n*def\s+(\w*)\s*\((.*)\))')

    REGEX_GROUP_RAW_FUNCTION = 0

    def __init__(self, groovy_file_path):

        self.groovy_file = self._validate_file(groovy_file_path)
        self.file_content = self.get_file_content()
        self.groovy_functions = collections.OrderedDict()
        self.parse_groovy_content()

    @staticmethod
    def _validate_file(file_path):
        valid_file_path = None
        if os.path.exists(file_path):
            valid_file_path = os.path.normpath(file_path)
        return valid_file_path

    def get_file_content(self):
        groovy_file_content = None
        with open(self.groovy_file, 'r') as file_obj:
            groovy_file_content = file_obj.read()
        return groovy_file_content

    def parse_groovy_content(self):
        groovy_functions_found = re.findall(self.REGEX_GROOVYDOC_FUNCTION, self.file_content)
        for groovy_function_string in groovy_functions_found:
            raw_body_function = groovy_function_string[self.REGEX_GROUP_RAW_FUNCTION]
            new_function = GroovyFunction(raw_body_function)
            self.groovy_functions[new_function.name] = new_function

    def get_groovy_functions(self):
        # type: () -> dict[str, GroovyFunction]
        return self.groovy_functions


class GroovyFunction(object):

    REGEX_GROOVYDOC_FUNCTION_DEF = re.compile(r'(def\s+(\w*)\((.*)\))')
    REGEX_GROOVYDOC_PARAMETERS = re.compile(r'(@param\s+(\w*)\s+(.*))')
    REGEX_GROOVYDOC_RETURN = re.compile(r'(@return\s+(.*))')

    REGEX_GROUP_PARAMETER_BODY = 0
    REGEX_GROUP_RETURN = 0

    def __init__(self, function_docstring):

        self.raw_docstring = function_docstring
        self.formatted_docstring = self.__get_formatted_docstring(function_docstring)
        self.header = None
        self.description = None
        self.name = None
        self.code_definition = None
        self.parameters = collections.OrderedDict()
        self.returns = None
        self.parse_docstring_body()
        self.parse_function_definition()

    @staticmethod
    def __get_formatted_docstring(raw_docstring):
        # type: (str) -> str
        docstring_lines = raw_docstring.split('\n')
        formatted_docstring = ''
        re_format_string = re.compile(r'\s*\*+\s*(.*)')
        for line in docstring_lines:
            if re.match(re_format_string, line):
                formatted_line = re.search(re_format_string, line)
                formatted_docstring += formatted_line.group(1) + '\n'
        return formatted_docstring

    def parse_docstring_body(self):

        # Parse and Instance Parameters
        # ----------------------------------------------------------------------
        parameters_found = re.findall(self.REGEX_GROOVYDOC_PARAMETERS, self.raw_docstring)
        # search for all parameters
        for parameter_string_found in parameters_found:
            parameter_str_body = parameter_string_found[self.REGEX_GROUP_PARAMETER_BODY]
            new_parameter = GroovyParameter(parameter_str_body)
            self.parameters[new_parameter.name] = new_parameter

        # Parse Return
        # ----------------------------------------------------------------------
        return_found = re.findall(self.REGEX_GROOVYDOC_RETURN, self.raw_docstring)
        if return_found:
            self.returns = return_found[0][self.REGEX_GROUP_RETURN]
        else:
            self.returns = "Nothing."

        # Parse Description
        # ----------------------------------------------------------------------
        description_only = self.formatted_docstring
        description_only = re.sub(self.REGEX_GROOVYDOC_PARAMETERS, '', description_only).strip()
        description_only = re.sub(self.REGEX_GROOVYDOC_RETURN, '', description_only).strip()
        self.description = description_only

        self.header = self.description.split('\n')[0]

    def parse_function_definition(self):

        # Parse Return
        # ----------------------------------------------------------------------
        function_def_found = re.findall(self.REGEX_GROOVYDOC_FUNCTION_DEF, self.raw_docstring)
        if function_def_found:
            raw_function_def_found = function_def_found[0]
            self.name = raw_function_def_found[1]
            self.code_definition = "def {f_name}( {param_content} )".format(
                f_name=self.name,
                param_content=raw_function_def_found[2]
            )

    def description_confluence_format(self):
        # type: () -> str
        formatted_lines = self.description.split('\n')
        html_format = ''
        html_format += '<p><code>\n'
        for line in formatted_lines:
            html_format += '{raw_line}<br/>'.format(raw_line=line)
        html_format += '</code></p>\n'
        return html_format


class GroovyParameter(object):

    REGEX_GROOVYDOC_PARAMETER_FORMAT = re.compile(r'(@param\s+(\w*)\s+\(?(\w*)\)?\s+(.*))')

    REGEX_GROUP_PARAM_NAME = 1
    REGEX_GROUP_PARAM_TYPE = 2
    REGEX_GROUP_PARAM_DESC = 3

    def __init__(self, parameter_docstring):

        self.body = parameter_docstring
        self.name = None
        self.type = None
        self.description = None
        self.parse_parameter()

    def parse_parameter(self):
        parameters_found = re.findall(self.REGEX_GROOVYDOC_PARAMETER_FORMAT, self.body)
        for parameter_string_found in parameters_found:
            self.name = parameter_string_found[self.REGEX_GROUP_PARAM_NAME]
            self.type = parameter_string_found[self.REGEX_GROUP_PARAM_TYPE]
            self.description = parameter_string_found[self.REGEX_GROUP_PARAM_DESC]

    def confluence_format(self):
        # type: () -> str
        html_format = """
        <span style="color: rgb(0,0,255);">
            <strong>{p_name}</strong>
        </span>
        <code>{p_type}</code> - <em>{p_desc}</em>
        """.format(
            p_name=self.name,
            p_type=self.type,
            p_desc=self.description
        )
        return html_format

# class ConfluenceHtmlElement(object):
#
#     def __init__(self, string_element, html_format='{}'):
#         # type: (str, str) -> ConfluenceHtmlElement
#         self.string_element = None
#         self.html_format = html_format
#         self.html_element = None
#         self._format_element()
#
#     def to_html(self):
#         # type: () -> str
#         return self.html_element
#
#     def to_string(self):
#         # type: () -> str
#         return self.string_element
#
#     def _format_element(self):
#         self.html_element = self.html_format.format(self.string_element)
#
#     def __str__(self):
#         return self.string_element
