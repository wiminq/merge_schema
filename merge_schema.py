#!/usr/bin/env python

import sys, time, re
try:
        from optparse import OptionParser
        import os
except ImportError:
        print >> sys.stderr, """\

There was a problem importing one of the Python modules required to run yum.
The error leading to this problem was:

%s

Please install a package which provides this module, or
verify that the module is installed correctly.

It's possible that the above module doesn't match the current version of Python,
which is:

%s

""" % (sys.exc_value, sys.version)
        sys.exit(1)

__prog__= "merge_schema"
__version__="0.1-beta"


def config_option():
    usage =  "usage: %prog [options] arg \n"
    usage += " e.g.: %prog -f from_schema.sql -t to_schema.sql -o merge_schema.sql"
    parser = OptionParser(usage)
    parser.add_option("-f","--from",dest="from_schema",help="from database schema file")
    parser.add_option("-t","--to",dest="to_schema",help="to database schema file")
    parser.add_option("-o","--out",dest="merge_alters",help="output merge alters")

    (options, args) = parser.parse_args()

    if not options.from_schema or not options.to_schema or not options.merge_alters:
        parser.error("You must input -f and -t and -o parameters");

    global opt_main
    opt_main = {}
    opt_main["from_schema"] = options.from_schema
    opt_main["to_schema"] = options.to_schema
    opt_main["merge_alters"] = options.merge_alters

class SchemaObjects(object):
    def __init__(self,from_schema,to_schema):
        self.from_schema = from_schema
        self.to_schema   = to_schema
        self.run()

    def run(self):
        self.objects_alters = ''
        self.return_objects = {}
        self.return_objects['tables'] = {}
        self.return_objects['servers'] = {}
        self.return_objects['events'] = {}
        self.return_objects['routines'] = {}
        self.return_objects['triggers'] = {}

        self.from_tables = self._get_tables(self.from_schema)
        self.to_tables = self._get_tables(self.to_schema)
        self.diff_tables = self._get_diff_tables(self.from_tables,self.to_tables)
        for table in self.diff_tables:
            self.return_objects['tables'][table] = {}
            self.return_objects['tables'][table]['from_table'] = self._get_table_definitions(self.diff_tables[table]['from_table'])
            self.return_objects['tables'][table]['to_table']   = self._get_table_definitions(self.diff_tables[table]['to_table'])

    def _record_alters(self,alter):
        self.objects_alters += alter
        self.objects_alters += "\n"
        print alter

    def get_objects_alters(self):
        return self.objects_alters

    def get_schema_objects(self):
        return self.return_objects

    def _get_servers(self,schema_name):
        pass

    def _get_events(self,schema_name):
        pass

    def _get_routines(self,schema_name):
        pass

    def _get_triggers(self,schema_name):
        pass

    def _get_tables(self,schema_name):
        try:
            schema_file = open(schema_name, 'r')
        except IOError:
            print 'Cannot open file', schema_name
        else:
            schema_file.readline()
            schema_string = ''
            for line in schema_file:
                schema_string = schema_string + line
            schema_file.close()
            return_tables = {}
            tables = re.findall(r"CREATE TABLE[^;]*;", schema_string)
            for table in tables:
                table_name = re.match(r"(CREATE TABLE \`)(.*)(\` \()", table)
                if table_name:
                    return_tables[table_name.group(2)] = table

            return return_tables

    def _get_diff_tables(self,from_tables,to_tables):
        return_tables = {}
        if from_tables and to_tables:
            for table in from_tables:
                if to_tables.has_key(table):
                    if from_tables[table] == to_tables[table]:
                        pass
                    else:
                        return_tables[table] = {}
                        return_tables[table]['from_table'] = from_tables[table]
                        return_tables[table]['to_table'] = to_tables[table]
                else:
                     self._record_alters("-- %s" % (table))
                     self._record_alters("drop table %s;" % (table))
                     self._record_alters(" ")

            for table in to_tables:
                if from_tables.has_key(table):
                    pass
                else:
                    self._record_alters("-- %s" % (table))
                    self._record_alters("%s" % (to_tables[table]))
                    self._record_alters(" ")

        return return_tables

    def _get_table_definitions(self,schema_table):
        return_definitions = {}
        return_definitions['column'] = {}
        return_definitions['primary'] = {}
        return_definitions['unique'] = {}
        return_definitions['key'] = {}
        return_definitions['foreign'] = {}
        return_definitions['fulltext'] = {}
        return_definitions['option'] = {}

        table_definitions = schema_table.split('\n')

        for definition in table_definitions:
            column_name = re.match(r"(\s*\`)([^`]*)(\`.*)", definition)
            if column_name:
                return_definitions['column'][column_name.group(2)] = re.match(r"([^`]*)([^,]*)(,?)", definition).group(2)

            primary_name = re.match(r"(\s*PRIMARY KEY\s*)", definition)
            if primary_name:
                return_definitions['primary']['primary'] = re.match(r"(\s*)(PRIMARY KEY \(.*\))(,?)", definition).group(2)

            unique_name = re.match(r"(\s*UNIQUE KEY \`)([^`]*)(\`.*)", definition)
            if unique_name:
                return_definitions['unique'][unique_name.group(2)] = re.match(r"(\s*)(UNIQUE KEY.*\))(,?)", definition).group(2)

            key_name = re.match(r"(\s*KEY \`)([^`]*)(\`.*)", definition)
            if key_name:
                return_definitions['key'][key_name.group(2)] = re.match(r"(\s*)(KEY.*\))(,?)", definition).group(2)

            foreign_name = re.match(r"(\s*CONSTRAINT \`)([^`]*)(\`.*)", definition)
            if foreign_name:
                return_definitions['foreign'][foreign_name.group(2)] = re.match(r"(\s*)(CONSTRAINT[^,]*)(,?)", definition).group(2)

            fulltext_name = re.match(r"(\s*FULLTEXT KEY \`)([^`]*)(\`.*)", definition)
            if fulltext_name:
                return_definitions['fulltext'][fulltext_name.group(2)] = re.match(r"(\s*)(FULLTEXT KEY.*\))(,?)", definition).group(2)

            option_name = re.match(r"(\)\s*ENGINE=.*)", definition)
            if option_name:
                return_definitions['option']['option'] = re.match(r"(\)\s*)(ENGINE[^;]*)(;?)", definition).group(2)

        return return_definitions

class SchemaAlters(object):
    def __init__(self,schema_objects):
        self.diff_objects = schema_objects
        self.run()

    def run(self):
        self.definitions_alters = ''
        self.return_alters = {}
        self.return_alters['tables'] = {}
        self.return_alters['servers'] = {}
        self.return_alters['events'] = {}
        self.return_alters['routines'] = {}
        self.return_alters['triggers'] = {}
        self._alter_tables(self.diff_objects['tables'])

    def _record_alters(self,alter):
        self.definitions_alters += alter
        self.definitions_alters += "\n"
        print alter

    def get_definitions_alters(self):
        return self.definitions_alters

    def _alter_tables(self,schema_tables):
        for table in schema_tables:
            self._record_alters("-- %s" % (table))
            from_table = schema_tables[table]['from_table']
            to_table = schema_tables[table]['to_table']

            self._column(table,from_table['column'],to_table['column'])
            self._primary(table,from_table['primary'],to_table['primary'])
            self._unique(table,from_table['unique'],to_table['unique'])
            self._key(table,from_table['key'],to_table['key'])
            self._foreign(table,from_table['foreign'],to_table['foreign'])
            self._fulltext(table,from_table['fulltext'],to_table['fulltext'])
            self._option(table,from_table['option'],to_table['option'])
            self._record_alters(" ")

    def _column(self,table,from_column,to_column):
        for definition in from_column:
            if to_column.has_key(definition):
                if from_column[definition] == to_column[definition]:
                    pass
                else:
                    self._record_alters("alter table `%s` modify column %s;" % (table,to_column[definition]))
            else:
                self._record_alters("alter table `%s` drop column `%s`;" % (table,definition))

        for definition in to_column:
            if from_column.has_key(definition):
                pass
            else:
                self._record_alters("alter table `%s` add column `%s`;" % (table,to_column[definition]))

    def _primary(self,table,from_primary,to_primary):
        if from_primary.has_key('primary'):
            if to_primary.has_key('primary'):
                if from_primary['primary'] == to_primary['primary']:
                    pass
                else:
                    self._record_alters("alter table `%s` drop primary key;" % (table))
                    self._record_alters("alter table `%s` add %s;" % (table,to_primary['primary']))
            else:
                self._record_alters("alter table `%s` drop primary key;" % (table))

        if to_primary.has_key('primary'):
            if from_primary.has_key('primary'):
                pass
            else:
                self._record_alters("alter table `%s` add %s;" % (table,to_primary['primary']))

    def _unique(self,table,from_unique,to_unique):
        for definition in from_unique:
            if to_unique.has_key(definition):
                if from_unique[definition] == to_unique[definition]:
                    pass
                else:
                    self._record_alters("alter table `%s` drop unique key %s;" % (table,definition))
                    self._record_alters("alter table `%s` add %s;" % (table,to_unique[definition]))
            else:
                self._record_alters("alter table `%s` drop unique key %s;" % (table,definition))

        for definition in to_unique:
            if from_unique.has_key(definition):
                pass
            else:
                self._record_alters("alter table `%s` add %s;" % (table,to_unique[definition]))

    def _key(self,table,from_key,to_key):
        for definition in from_key:
            if to_key.has_key(definition):
                if from_key[definition] == to_key[definition]:
                    pass
                else:
                    self._record_alters("alter table `%s` drop key %s;" % (table,definition))
                    self._record_alters("alter table `%s` add key %s;" % (table,to_key[definition]))
            else:
                self._record_alters("alter table `%s` drop key %s;" % (table,definition))

        for definition in to_key:
            if from_key.has_key(definition):
                pass
            else:
                self._record_alters("alter table `%s` add key %s;" % (table,to_key[definition]))

    def _foreign(self,table,from_foreign,to_foreign):
        for definition in from_foreign:
            if to_foreign.has_key(definition):
                if from_foreign[definition] == to_foreign[definition]:
                    pass
                else:
                    self._record_alters("alter table `%s` drop foreign key `%s`;" % (table,definition))
                    self._record_alters("alter table `%s` add %s;" % (table,to_foreign[definition]))
            else:
                self._record_alters("alter table `%s` drop foreign key `%s`;" % (table,definition))

        for definition in to_foreign:
            if from_foreign.has_key(definition):
                pass
            else:
                self._record_alters("alter table `%s` add %s;" % (table,to_foreign[definition]))

    def _fulltext(self,table,from_fulltext,to_fulltext):
        for definition in from_fulltext:
            if to_fulltext.has_key(definition):
                if from_fulltext[definition] == to_fulltext[definition]:
                    pass
                else:
                    self._record_alters("alter table `%s` drop fulltext key `%s`;" % (table,definition))
                    self._record_alters("alter table `%s` add %s;" % (table,to_fulltext[definition]))
            else:
                self._record_alters("alter table `%s` drop fulltext key `%s`;" % (table,definition))

        for definition in to_fulltext:
            if from_fulltext.has_key(definition):
                pass
            else:
                self._record_alters("alter table `%s` add %s;" % (table,to_fulltext[definition]))

    def _option(self,table,from_option,to_option):
        if from_option.has_key('option'):
            if to_option.has_key('option'):
                if from_option['option'] == to_option['option']:
                    pass
                else:
                    self._record_alters("alter table `%s` %s;" % (table,to_option['option']))


def main():
    config_option()

    current_objects = SchemaObjects(opt_main["from_schema"],opt_main["to_schema"])
    schema_objects = current_objects.get_schema_objects()
    objects_alters = current_objects.get_objects_alters()

    current_alters = SchemaAlters(schema_objects)
    definitions_alters = current_alters.get_definitions_alters()

    merge_alters = open(opt_main["merge_alters"],'w')
    merge_alters.write(objects_alters)
    merge_alters.write(definitions_alters)
    merge_alters.close()

if __name__ == "__main__":
    main()
