import os


def _parse_fp_lib_table(string: str) -> tuple(int, tuple(str, list)):
    index = 0
    size = 0
    subs = None

    while string[index] != '(':
        index += 1
        if index == len(string):
            return string

    index += 1
    string = string[index:]
    size = index
    index = 0

    while string[index] != ')':
        if string[index] == '(':
            sub_size, sub = _parse_fp_lib_table(string[index:])

            if subs is None:
                subs = []
            subs.append(sub)

            string = string[:index] + string[index + sub_size:]

            size += sub_size
        else:
            index += 1
            size += 1

        if index >= len(string):
            raise Exception('No closing bracket found')

    this = string[:index]
    size += 1

    return size, (this, subs)


def parse_fp_lib_table_braces(string: str) -> tuple(str, list):
    return _parse_fp_lib_table(string)[1]


def open_fp_lib_table(path: str or os.path) -> str:
    fp_lib_table = os.path.join(path, 'fp-lib-table')

    if not os.path.exists(fp_lib_table):
        return None

    with open(fp_lib_table, 'r') as f:
        return f.read()


class FpLibTableLib():
    def __init__(self, name: str, type: str, uri: str, options: str, descr: str) -> None:
        self.name = name
        self.type = type
        self.uri = uri
        self.options = options
        self.descr = descr

    @classmethod
    def fromLst(cls, value_list: list(tuple(str, list))) -> 'FpLibTableLib':
        name = ''
        type = ''
        uri = ''
        options = ''
        descr = ''

        for value in value_list:
            keyword, value = value[0].split(' ')
            value = value.strip('"')

            if keyword == 'name':
                name = value
            elif keyword == 'type':
                type = value
            elif keyword == 'uri':
                uri = value
            elif keyword == 'options':
                options = value
            elif keyword == 'descr':
                descr = value

        return cls(name, type, uri, options, descr)

    def __str__(self) -> str:
        return f'(lib (name "{self.name}")(type "{self.type}")(uri "{self.uri}")(options "{self.options}")(descr "{self.descr}"))'


class FpLibTable():
    def __init__(self, libs: list=[]) -> None:
        self.libs = libs

    @classmethod
    def fromStr(cls, str: str) -> 'FpLibTable':
        if str is None:
            return cls()

        parsed = parse_fp_lib_table_braces(str)

        if parsed[0].strip() != 'fp_lib_table':
            raise ValueError('Not a fp_lib_table')

        libs = []
        for sub_parse in parsed[1]:
            if sub_parse[0].strip() == 'lib':
                libs.append(FpLibTableLib.fromLst(sub_parse[1]))

        return cls(libs)

    def __str__(self) -> str:
        string = '(fp_lib_table\n'
        for lib in self.libs:
            string += f'  {lib}\n'
        string += ')\n'
        return string