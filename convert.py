#!/usr/bin/python
# -*- coding: utf-8 -*-

# Update Version with all changes
VERSION = '2015.1.0'

# Defaults
SOURCE_FOLDER   = "source"
DEST_FOLDER     = "upload"
LOG_FOLDER      = "logs"

LOG_FILE_NAME       = 'story_data_prep.log'
OUTPUT_FILE_NAME    = 'upload.csv'

DESTINATION_KEY         = 'destination'
SOURCE_KEY              = 'source'
CONVERSION_FUNCTION_KEY = 'conversion'
SOURCE_INDEX_KEY        = 'index'

PROCESSING_COUNT_FEEDBACK   = 100
MIN_EXPIRATION_DATE_YEAR    = 10
SOURCE_DATE_FORMAT          = '%m/%d/%Y %I:%M:%S %p'
BULLET_LIST_FORMAT          = u"<ul type=\"disc\"><li>{0}</li><li>{1}</li><li>{2}</li></ul>"
CSV_SEP                     = u','
EDT_OFFSET                  = '+04:00'
EST_OFFSET                  = '+05:00'
NO_STATE_INFO_TEXT          = u'No State Information'
US_STATES = {
        u'AK': u'Alaska',
        u'AL': u'Alabama',
        u'AR': u'Arkansas',
        u'AS': u'American Samoa',
        u'AZ': u'Arizona',
        u'CA': u'California',
        u'CO': u'Colorado',
        u'CT': u'Connecticut',
        u'DC': u'District of Columbia',
        u'DE': u'Delaware',
        u'FL': u'Florida',
        u'GA': u'Georgia',
        u'GU': u'Guam',
        u'HI': u'Hawaii',
        u'IA': u'Iowa',
        u'ID': u'Idaho',
        u'IL': u'Illinois',
        u'IN': u'Indiana',
        u'KS': u'Kansas',
        u'KY': u'Kentucky',
        u'LA': u'Louisiana',
        u'MA': u'Massachusetts',
        u'MD': u'Maryland',
        u'ME': u'Maine',
        u'MI': u'Michigan',
        u'MN': u'Minnesota',
        u'MO': u'Missouri',
        u'MP': u'Northern Mariana Islands',
        u'MS': u'Mississippi',
        u'MT': u'Montana',
        u'NA': u'National',
        u'NC': u'North Carolina',
        u'ND': u'North Dakota',
        u'NE': u'Nebraska',
        u'NH': u'New Hampshire',
        u'NJ': u'New Jersey',
        u'NM': u'New Mexico',
        u'NV': u'Nevada',
        u'NY': u'New York',
        u'OH': u'Ohio',
        u'OK': u'Oklahoma',
        u'OR': u'Oregon',
        u'PA': u'Pennsylvania',
        u'PR': u'Puerto Rico',
        u'RI': u'Rhode Island',
        u'SC': u'South Carolina',
        u'SD': u'South Dakota',
        u'TN': u'Tennessee',
        u'TX': u'Texas',
        u'UT': u'Utah',
        u'VA': u'Virginia',
        u'VI': u'Virgin Islands',
        u'VT': u'Vermont',
        u'WA': u'Washington',
        u'WI': u'Wisconsin',
        u'WV': u'West Virginia',
        u'WY': u'Wyoming'
}

# -------------------------------- Logging Messages ------------------------

LOG_MSG_STARTING        = "Starting Conversion"
LOG_MSG_SCRIPT_VERSION  = "Script Version: {0}"
LOG_MSG_USING_LOG       = "Using log file: {0}"
LOG_MSG_PYTHON_VER      = "Program will only run on Python Version 2.6 or 2.7"
LOG_MSG_PROG_ABORT      = "Program aborted: {0}"
LOG_MSG_VERIFY_BEGIN    = "Verifying conversion..."
LOG_MSG_VERIFY_COUNT    = "Source records: {0}, Destination Records: {1}"
LOG_MSG_VERIFY_SUCCESS  = "Verification Result: Pass"
LOG_MSG_VERIFY_FAIL     = "Verification Result: Fail"

LOG_MSG_CREATE_MAPPINGS     ="Creating rules from mappings."
LOG_MSG_ADD_RULE            ="Added rule for '{0}' mapping."
LOG_MSG_PROCESS_RECS        ="Processed {0} records."
LOG_MSG_PROC_COMPLETE       ="Processed {0} records. Conversion Complete"
LOG_MSG_SRC_NOT_FOUND       = u"Source column '{0}' not found in file. Aborting program."
LOG_MSG_GET_SRC_COL_IDX     = u"Retrieving source column indices for {0} field."
LOG_MSG_SRC_DIR_NOT_FOUND   = "Source Directory '{0}' not found - application will terminate."
LOG_MSG_USING_SRC_DIR       = "Using source folder: {0}"
LOG_MSG_USING_DEST_FLDR     = "Using destination folder: {0}"
LOG_MSG_ABORT_NO_SRC_FILE   = "Aborting program: No conversion files found in folder {0}"
LOG_MSG_PROCESS_FROM_TO     = "Processing files from source: {0} to destination: {1}."


#Exception Messages
LOG_MSG_EXCEPT_DIR_NOT_FOUND = "Source Directory not found.  Aborting program."
LOG_MSG_EXCEPT_NO_SRC       = "Aborting program. Source files missing."
LOG_MSG_EXCEPT_SRC_FLD_NOT_FOUND = "Aborting program - source field not found in file"

VERSION_SYS_ARG = '--version'

import os
import logging
import sys
import datetime
import io


# -------------------------------------------     LOGGING SETUP -----------------------------------------------------
#  initialize the logging...use stdout for console logging

logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(logFormatter)

rootLogger.addHandler(consoleHandler)
rootLogger.setLevel(logging.INFO)

# ------------------------------------------- Global Functions ------------------------------------------------------


def get_version():
    return VERSION

# ------------------------------------------ Conversion Functions -------------------------------------------------
# These function are used in the MAPPING dictionary list and ConversionRule objects
#
# All functions assume a single parameter containing of a list of values: def fn([...])


def date_to_iso_date(field_list):
    """ Converts a date in the format: SOURCE_DATE_FORMAT
        to an ISO date.

        :param  field_list - a list containing a single date
        :return unicode string of the ISO formatted date
    """
    in_date = field_list[0]
    new_date = datetime.datetime.strptime(in_date, SOURCE_DATE_FORMAT)
    result_date = convert_date_to_utc(new_date)
    return result_date


def currency_to_integer(field_list):
    """ Converts a currency value in the format: $##.##
        to an integer.

        :param  field_list - a list containing a single string with a '$' sign
                followed by a decimal number
        :return unicode string of the value trimmed for whitespace
                '$' sign removed and converted to an integer
    """
    amount = field_list[0]
    amount_as_num = amount.strip()[1:]
    return unicode(int(float(amount_as_num)))


def year_month_to_date(field_list):
    """ Converts yy and mm value to an ISO date.

        :param  field_list - a list containing two entries, First entry
                is the yy value, second entry is the mm value.
                Note: yy and mm must be present and yy must be at 2 characters
        :return unicode string of the ISO formatted date if the yy and mm
                values are valid. Empty string otherwise
    """
    # logic: since we only have the year and month, the tag is valid
    # until midnight of the last day of the next month. So get midnight of
    # first day of following month and subtract one day!
    result = None
    yy = field_list[0]
    mm = field_list[1]
    if len(yy) > 1 and len(mm) > 0:
        year , month = int(yy) + 2000 , int(mm)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        # just before midnight 23:59:59
        the_date = datetime.datetime(year,month,1,23,59,59)
        one_day = datetime.timedelta(days=1)
        result = the_date - one_day
        result_date = convert_date_to_utc(result)

        return result_date

    else:
        return u''


def to_bullet_list(field_list):
    """ Converts 3 fields to a bulleted HTML list.

        :param  field_list - a list containing three entries, second entry
                is a US State abbreviation and is converted to the full name of
                the state.
        :return unicode string of the HTML bulleted list
    """
    state = state_code_to_full(field_list[1])
    result = BULLET_LIST_FORMAT.format(field_list[0], state, field_list[2])
    return result

# --------------------- Conversion Function Helper Functions --------------------------


def state_code_to_full(state_code):
    """ Converts a state two letter code to the full state name.

        :param  two character unicode state abbreviation.
        :return unicode string of the full state name, NO_STATE_INFO_TEXT string if
                not a valid US State
    """
    if US_STATES.has_key(state_code):
        return US_STATES[state_code]
    else:
        return NO_STATE_INFO_TEXT


def convert_date_to_utc(the_date):
    # converts local file to YYYY-MM-DDTHH:MM:SS+04:00 etc
    # MD: date times are all in EST or EDT.
    result = u''
    edt_offset = datetime.timedelta(hours=4)
    est_offset = datetime.timedelta(hours=5)

    # Since all dates are > 2010: get 2nd Sunday in march and 1st Sunday in Nov for given year
    year = the_date.year
    from_date = datetime.datetime(year,3,1)
    from_date = get_second_sunday(from_date)
    to_date = datetime.datetime(year,11,1)
    to_date = get_first_sunday(to_date)
    # now establish if the date is in the fall/winter or spring/summer
    if to_date > the_date >= from_date:
        the_date -= edt_offset
        result = unicode(the_date.isoformat() + EDT_OFFSET)
    else:
        the_date -= est_offset
        result = unicode(the_date.isoformat() + EST_OFFSET)

    return result


def get_first_sunday(from_date):
    one_day = datetime.timedelta(days=1)
    from_date += one_day
    while from_date.isoweekday() != 7:
        from_date += one_day
    return from_date


def get_second_sunday(from_date):
    new_date = get_first_sunday(from_date)
    new_date = get_first_sunday(new_date)
    return new_date


#--------------------- Field Mapping: List of Dictionary entries ---------------------
# Each entry: { DESTINATION_KEY: <Rally Field>,
#               SOURCE_KEY :<list of source columns>,
#               CONVERSION_FUNCTION_KEY : <function>
#             }
# NOTE: To change/add a mapping, add/update the mapping dictionary and provide the appropriate conversion function.

RALLY_MAPPING   = [{DESTINATION_KEY: u'Name',                SOURCE_KEY :[u'citation'],             CONVERSION_FUNCTION_KEY : None} ,
                   {DESTINATION_KEY: u'Description',         SOURCE_KEY :[u'Description'],          CONVERSION_FUNCTION_KEY : None } ,
                   {DESTINATION_KEY: u'ViolationDate',       SOURCE_KEY :[u'violDate'],             CONVERSION_FUNCTION_KEY : date_to_iso_date },
                   {DESTINATION_KEY: u'PlanEstimate',        SOURCE_KEY :[u'violFine'],             CONVERSION_FUNCTION_KEY : currency_to_integer },
                   {DESTINATION_KEY: u'LicenseExpiration',   SOURCE_KEY :[u'expyy',u'expmm'],       CONVERSION_FUNCTION_KEY : year_month_to_date },
                   {DESTINATION_KEY: u'Notes',               SOURCE_KEY :[u'make',u'state',u'tag'], CONVERSION_FUNCTION_KEY : to_bullet_list }]


# ------------------------ Validation Rules --------------------------------

def validate_row_counts(source_file, destination_file):
    # simple row count validation
    success = False
    with io.open(source_file, 'r', encoding='utf-8') as src_file, \
                            io.open(destination_file, 'r', encoding='utf-8') as dest_file:
        count_source = sum(1 for _ in src_file)
        count_dest = sum(1 for _ in dest_file)
        success = (count_source == count_dest)
        rootLogger.info(LOG_MSG_VERIFY_COUNT.format(count_source, count_dest))
    return success

# ----------------------  Classes ------------------------------------------

"""
Class:  ConversionRule

        This class encapsulates the single entry from a mapping list which holds the transformation logic.

        As each line of the source file is processed, the rule is updated to insert the data from the row columns.
        The 'execute' method then performs the transformation from source field(s) to destination field

        :param  output_column_index: position of the output in the destination file (Integer)
        :param  destination_field: name of the column in the destination file (string)
        :param  source_columns: list of the source column used to create the destination value (list)
        :param  conversion_function: function that takes a single parameter of type list

"""


class ConversionRule(object):
    def __init__(self, output_column_index, destination_field, source_columns, conversion_function=None):
        self._output_column_index = output_column_index
        self._destination_field = destination_field
        self._source_fields = source_columns
        self._convert_function = conversion_function
        self._source_data_indexes = []
        self._data_list = []

    @property
    def source_data_indexes(self):
        return self._source_data_indexes

    @source_data_indexes.setter
    def source_data_indexes(self, value):
        self._source_data_indexes = value

    @property
    def data_list(self):
        return self._data_list

    @data_list.setter
    def data_list(self, value):
        self._data_list = value

    def execute(self):
        # if no conversion routine we just send the data as is.
        result = self._data_list[0]
        if self._convert_function:
            result = self._convert_function(self._data_list)
        return result

    @property
    def source_columns(self):
        return self._source_fields

    @property
    def output_column_name(self):
        return self._destination_field


"""
Class:  Converter

        This class performs the transformation from source file to destination file.
        Note: A converter has no knowledge of the transformation logic, this is encapsulated in the
        ConversionRule objects

        On initialization, a conversion rule is created for each entry in the mapping list.

        The transform method performs the transformation from source to destination:
        Once the source file is opened for processing and the row headings established,
        the rules are updated to establish the column positions of the source column fields.
        For each row in the source file, the rules fetch the relevant data from the mapped columns
        then their execute method is called to perform the transformation.  The data from all rule transformations
        is then concatenated to a comma delimited line to be output to the destination file.

        :param  source_file: source file path
        :param  destination_file: destination file path
        :param  mapping_list: list of mappings of the form:
            {DESTINATION_KEY: <Rally Field>, SOURCE_KEY :<list of source columns>,CONVERSION_FUNCTION_KEY : <function>}
        :param  validation_fn_list: list of functions of form f(source_file_path, dest_file_path) that return True/False
                based on validation of files.


        TODO: This should be decoupled from the file read/write. Using an abstract dataSource and dataSink type
        interface rather than file names would allow the solution to source and sink data from streams, files, APIs, etc
"""


class Converter(object):
    def __init__(self, source_file, destination_file, mapping_list, validation_fn_list):
        self.source_file = source_file
        self.destination_file = destination_file
        self.rules = []
        self.source_headers = []
        self.validation_fns = validation_fn_list

        rootLogger.info(LOG_MSG_CREATE_MAPPINGS)
        for idx, mapping in enumerate(mapping_list):
            rally_field = mapping[DESTINATION_KEY]
            function    = mapping[CONVERSION_FUNCTION_KEY]
            source_cols = mapping[SOURCE_KEY]

            new_rule = ConversionRule(idx, rally_field, source_cols, function)
            self.rules.append(new_rule)
            rootLogger.info(LOG_MSG_ADD_RULE.format(rally_field))

    def transform(self):
        first_line = True
        line_count = 0
        with io.open(self.source_file, 'r', encoding='utf-8') as src_file, \
                            io.open(self.destination_file, 'w+', encoding='utf-8') as dest_file:
            for line in src_file.readlines():
                line = line.rstrip('\n')
                if first_line:
                    first_line = False
                    self._update_rules_source_data_indexes(line)
                    header_row = self._get_destination_header_line()
                    dest_file.write(header_row)
                else:
                    line_count += 1
                    # map the actual data into the rule based on the current line
                    line_data = line.split(CSV_SEP)
                    for rule in self.rules:
                        rule_field_data = []
                        column_indexes = rule.source_data_indexes
                        for idx in column_indexes:
                            data_value = line_data[idx]
                            rule_field_data.append(data_value)

                        rule.data_list = rule_field_data

                    # now we just execute the rules then concat the values and write to file
                    out_line_list = []
                    for rule in self.rules:
                        result = rule.execute()
                        out_line_list.append(result)

                    dest_file.write(CSV_SEP.join(out_line_list) + u'\n')

                    #show/log progress
                    if line_count % PROCESSING_COUNT_FEEDBACK == 0:
                        rootLogger.info(LOG_MSG_PROCESS_RECS.format(line_count))

        # and we're done
        rootLogger.info(LOG_MSG_PROC_COMPLETE.format(line_count))
        self._validate_transform()

    def _validate_transform(self):
        rootLogger.info(LOG_MSG_VERIFY_BEGIN)
        results = []
        for fn in self.validation_fns:
            result = fn(self.source_file, self.destination_file)
            results.append(result)

        success = (False not in results)

        if success:
            rootLogger.info(LOG_MSG_VERIFY_SUCCESS)
        else:
            rootLogger.info(LOG_MSG_VERIFY_FAIL)

    def _update_rules_source_data_indexes(self, line):
        # retrieve header names from source and update the rules with the
        # column positions of the rule's source fields
        self.source_headers = line.split(CSV_SEP)

        # Use first header line to establish each of the column offsets for each rule
        # this avoids hard coding the various column offsets
        for rule in self.rules:
            rootLogger.info(LOG_MSG_GET_SRC_COL_IDX.format(rule.output_column_name))
            column_positions = []
            fields = rule.source_columns
            for field in fields:
                idx = self._get_index_of_source_field(field)
                if idx == -1:
                    rootLogger.critical(LOG_MSG_SRC_NOT_FOUND.format(field))
                    raise Exception(LOG_MSG_EXCEPT_SRC_FLD_NOT_FOUND)
                column_positions.append(idx)

            rule.source_data_indexes = column_positions

    def _get_destination_header_line(self):
        #Each rule has its destination field name, just concat these
        header_list = []
        for rule in self.rules:
            header_list.append(rule.output_column_name)
        return CSV_SEP.join(header_list) + u'\n'

    def _get_index_of_source_field(self, field):
        idx = 0
        try:
            idx = self.source_headers.index(field)
        except:
            idx = -1
        return idx



"""
Class:  Configurations

        This class encapsulates the set up of the logs and destination directories,
        verifies the source folder exists and there is at least one file to process.

"""


class Configurations(object):
    def __init__(self):
        self._source_files = []
        self.source_folder = SOURCE_FOLDER
        self.dest_folder = DEST_FOLDER
        self.log_folder = LOG_FOLDER
        self.setup()

    def setup(self):
        self._setup_logging_file()
        self._setup_destination()

        # critical error - if no source folder available...
        if not os.path.isdir(self.source_folder):
            rootLogger.critical(LOG_MSG_SRC_DIR_NOT_FOUND.format(self.source_folder))
            raise Exception(LOG_MSG_EXCEPT_DIR_NOT_FOUND)

        rootLogger.info(LOG_MSG_USING_SRC_DIR.format(self.source_folder))
        self._setup_source_files()

    def _setup_destination(self):
        # destination (output) folder
        if not os.path.isdir(self.dest_folder):
            os.mkdir(self.dest_folder)
        rootLogger.info(LOG_MSG_USING_DEST_FLDR.format(self.dest_folder))

    def _setup_source_files(self):
        # get the list of source files
        for (_, _, source_files) in os.walk(self.source_folder):
            self._source_files = [self.source_folder + os.path.sep + file for file in source_files if file.endswith('.csv')]
        if len(self.source_files) == 0:
            rootLogger.critical(LOG_MSG_ABORT_NO_SRC_FILE.format(self.source_folder))
            raise Exception(LOG_MSG_EXCEPT_NO_SRC)

    def _setup_logging_file(self):
        # set up the log file
        if not os.path.isdir(self.log_folder):
            os.mkdir(self.log_folder)
        # set up the log file
        log_file = self.log_folder + os.path.sep + LOG_FILE_NAME

        fileHandler = logging.FileHandler(log_file)
        fileHandler.setFormatter(logFormatter)
        rootLogger.addHandler(fileHandler)
        rootLogger.info(LOG_MSG_SCRIPT_VERSION.format(get_version()))
        rootLogger.info(LOG_MSG_USING_LOG.format(log_file))

    @property
    def source_files(self):
        return self._source_files

    @property
    def destination_file_path(self):
        return self.dest_folder + os.path.sep + OUTPUT_FILE_NAME


if __name__ == "__main__":
    # Won't run version 3 (unicode stuff)
    if sys.version_info[0] == 3:
        rootLogger.info(LOG_MSG_PYTHON_VER)
        exit(1)

    # check if asking for version
    arg_count = len(sys.argv)
    if arg_count > 1:
        if sys.argv[1] == VERSION_SYS_ARG:
            print(get_version())
            exit(0)

    # run the conversion
    try:
        rootLogger.info(LOG_MSG_STARTING)

        config = Configurations()
        # assume single file, can add multiple files
        source = config.source_files[0]
        destination = config.destination_file_path

        rootLogger.info(LOG_MSG_PROCESS_FROM_TO.format(source, destination))
        validation_rules = [validate_row_counts]
        converter = Converter(source, destination, RALLY_MAPPING, validation_rules)
        converter.transform()

    except Exception as e:
        rootLogger.warning(LOG_MSG_PROG_ABORT.format(e))
        exit(1)
